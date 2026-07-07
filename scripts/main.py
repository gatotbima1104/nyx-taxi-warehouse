from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout

from scripts.taxi_extractor import TaxiExtractor
from utils.constants import (
    TAXI_DATA_FILENAME,
    TAXI_URL,
    TAXI_ZONE_LOOKUP_TABLE,
    TAXI_ZONE_LOOKUP_URL,
    POSTGRES_URL,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER
)
from scripts.database_connection import DatabaseConnection
from scripts.bronze_loader import BronzeLoader
from scripts.managers.schema_manager import SchemaManager
from scripts.managers.audit_manager import AuditManager
from scripts.bronze_loader import Layer
from utils.helpers import Helper

# database connection
connection = DatabaseConnection(
    POSTGRES_URL,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD
)
conn = connection.get_connection()

# schema
schema = SchemaManager(conn)
audit = AuditManager(conn)

def extract() -> list[str]:
    print("\n")
    extract_files = [
        (TAXI_URL, TAXI_DATA_FILENAME),
        (TAXI_ZONE_LOOKUP_URL, TAXI_ZONE_LOOKUP_TABLE)
    ]

    extractor = TaxiExtractor()
    downloaded_files = []

    for url, filename in extract_files:
        downloaded_files.append(
            extractor.extract(url, filename)
        )
    
    Helper.log(message="Extract successfully ...")
    return downloaded_files

def load_to_bronze():
    # L1 --> BRONZE LAYER
    loader = BronzeLoader(conn)
    start = datetime.now()
    
    try:
        schema.execute(Path('db/init/01_schema.sql'))
        schema.execute(Path('db/init/02_bronze_load.sql'))
        schema.execute(Path('db/init/06_audit.sql'))
        loader.load_data(Path("data/raw/raw_yellow_tripdata_2026_01.parquet"), "raw_taxi_trips", Layer.BRONZE)
        loader.load_data(Path("data/raw/taxi_zone_lookup.csv"), "raw_taxi_lookup", Layer.BRONZE)
        
        rows = schema.fetch("""
            SELECT COUNT(*)
            FROM bronze.raw_taxi_trips
        """)
        
        audit.log_pipeline(
            layer="bronze",
            process_name="load to bronze",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=rows,
            status="SUCCESS",
            message="[BRONZE] Bronze layer loaded successfully."
        )
        
        Helper.log(message="Ingest to Bronze successfully ...")
        
    except Exception as e:
        conn.rollback()
        audit.log_pipeline(
            layer="bronze",
            process_name="load to bronze",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=0,
            status="FAILED",
            message=f"[ERROR] {str(e)}"
        )
        raise
 
def transform_to_silver():
    # L2 --> SILVER LAYER
    start = datetime.now()
    try:
        silver_layer = [
            Path('db/init/03_silver_transform.sql'),
            *sorted(Path('db/schemas/silver').glob('*.sql'))
        ]
        schema.execute_many(silver_layer)
        
        rows_taxi_cleaned = schema.fetch("""
        SELECT COUNT(*) 
        FROM silver.taxi_trips_cleaned
        """)
        
        rows_data_quality_issues = schema.fetch("""
        SELECT COUNT(*) 
        FROM silver.data_quality_issues
        """)
        
        print(f'[LOAD TO SILVER] Loaded {rows_taxi_cleaned:,} valid rows ...')
        print(f'[LOAD TO SILVER] Loaded {rows_data_quality_issues:,} invalid rows ...')
         
        audit.log_pipeline(
            layer="silver",
            process_name="load valid data to silver",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=rows_taxi_cleaned,
            status="SUCCESS",
            message="[SILVER] Valid data loaded successfully."
        )
        
        audit.log_pipeline(
            layer="silver",
            process_name="load invalid data to silver",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=rows_data_quality_issues,
            status="SUCCESS",
            message="[SILVER] Invalid Data loaded successfully."
        )
        
        Helper.log(message="Transform to Silver successfully ... ")
        
    except Exception as e:
        conn.rollback()
        audit.log_pipeline(
            layer="silver",
            process_name="silver transform",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=0,
            status="FAILED",
            message=f"[ERROR] {str(e)}"
        )
        raise

def analytics_to_gold():
    # L3 --> GOLD LAYER
    start = datetime.now()
    
    try:
        gold_layer = [
            Path('db/init/04_gold_mart.sql'),
            *sorted(Path('db/schemas/gold').glob('*.sql'))
        ]
        schema.execute_many(gold_layer)
        
        audit.log_pipeline(
            layer="gold",
            process_name="load to gold mart",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=None,
            status="SUCCESS",
            message="[GOLD] Silver layer loaded successfully."
        )
        Helper.log(message="Analytics to Gold successfully ... ")
        
    except Exception as e:
        conn.rollback()
        audit.log_pipeline(
            layer="gold",
            process_name="load to gold mart",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=0,
            status="FAILED",
            message=f"[ERROR] {str(e)}"
        )
        raise

def create_views():
    # CREATE VIEWS
    schema.execute(Path('db/init/05_views.sql'))
    Helper.log(message="Views created successfully ... ")
    
def gold_analytics():
    # BUSINESS DATA MODELLING
    start = datetime.now()

    try:

        queries = sorted(
            Path("db/queries").glob("*.sql")
        )
        
        with open("logs/business_analytics.log", "w", encoding="utf-8") as log:
            with redirect_stdout(log):
                schema.report_many(queries)

        audit.log_pipeline(
            layer="gold",
            process_name="business analytics",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=None,
            status="SUCCESS",
            message="[ANALYTICS] Business queries executed successfully."
        )

        Helper.log(message="Business Analytics completed ...")

    except Exception as e:

        conn.rollback()

        audit.log_pipeline(
            layer="gold",
            process_name="business analytics",
            start_time=start,
            end_time=datetime.now(),
            rows_processed=0,
            status="FAILED",
            message=str(e)
        )

        raise
    
def pipeline_report():
    print("\n")
    print("=" * 80)
    print("                     NYC TAXI PIPELINE EXECUTION REPORT")
    print("=" * 80)

    with conn.cursor() as cur:

        # Summary setiap proses
        cur.execute("""
            SELECT
                layer,
                process_name,
                start_time,
                end_time,
                rows_processed,
                status,
                EXTRACT(EPOCH FROM (end_time - start_time)) AS duration
            FROM audit.logs
            ORDER BY run_id;
        """)

        logs = cur.fetchall()

        pipeline_start = logs[0][2]
        pipeline_end = logs[-1][3]
        total_duration = pipeline_end - pipeline_start

        print(f"Started  : {pipeline_start}")
        print(f"Finished : {pipeline_end}")
        print(f"Duration : {total_duration}")

        print("\n" + "-" * 80)
        print(
            f'{"Layer":<10}'
            f'{"Process":<30}'
            f'{"Rows":>15}'
            f'{"Time(s)":>12}'
            f'{"Status":>12}'
        )
        print("-" * 80)

        for layer, process, _, _, rows, status, duration in logs:
            rows = "-" if rows is None else f"{rows:,}"

            print(
                f"{layer:<10}"
                f"{process:<30}"
                f"{rows:>15}"
                f"{duration:>12.2f}"
                f"{status:>12}"
            )

        # Data quality
        cur.execute("""
            SELECT COUNT(*)
            FROM bronze.raw_taxi_trips
        """)
        raw = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM silver.taxi_trips_cleaned
        """)
        valid = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM silver.data_quality_issues
        """)
        invalid = cur.fetchone()[0]

        cur.execute("""
            SELECT
                error_type,
                COUNT(*)
            FROM silver.data_quality_issues
            GROUP BY error_type
            ORDER BY COUNT(*) DESC;
        """)
        reasons = cur.fetchall()

    print("\n" + "-" * 80)
    print("DATA QUALITY")
    print("-" * 80)

    print(f"Raw Records     : {raw:,}")
    print(f"Valid Records   : {valid:,}")
    print(f"Invalid Records : {invalid:,}")

    print("\nInvalid Reasons")

    for reason, total in reasons:
        print(f"  • {reason:<30} {total:,}")

    print("\n" + "=" * 80)
    print("Pipeline Status : SUCCESS")
    print("=" * 80)

if __name__ == '__main__':
    extract()
    load_to_bronze()
    transform_to_silver()
    analytics_to_gold()
    create_views()
    gold_analytics()
    pipeline_report()