from utils.helpers import Helper
from io import StringIO
from psycopg2.extensions import connection as PGConnection
from pandas import DataFrame
from enum import StrEnum
from datetime import datetime
from pathlib import Path

from scripts.managers import (
    SchemaManager,
    AuditManager
)

class Layer(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"

class BronzeLoader:
    def __init__(self, conn: PGConnection):
        self.conn = conn
        self.schema = SchemaManager(conn)
        self.audit = AuditManager(conn)

    def load_to_pg(self, filepath: str, table_name: str, layer: Layer | None = None):
        df = self._normalize_dtypes(Helper.load_file(filepath))
        buffer = StringIO()

        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        sql = f"""
        COPY bronze.{table_name}
        FROM STDIN
        WITH (FORMAT CSV)
        """
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.copy_expert(sql, buffer)

        self.conn.commit()

        print(
            f"[LOAD TO {'BRONZE' if layer == 'bronze' else 'SILVER' if layer == 'silver' else 'GOLD'}] successfully loaded {len(df):,} rows --> bronze.{table_name}"
        )

    def _normalize_dtypes(self, df: DataFrame):
        PANDAS_NULLABLE_INTS = [
            "VendorID",
            "passenger_count",
            "RatecodeID",
            "PULocationID",
            "DOLocationID",
            "payment_type",
        ]
        for column in PANDAS_NULLABLE_INTS:
            if column in df.columns:
                df[column] = df[column].astype("Int64")
        return df
    
    def load_to_bronze(self):
        start = datetime.now()
        
        try:
            self.schema.execute(Path('db/init/01_schema.sql'))
            self.schema.execute(Path('db/init/02_bronze_load.sql'))
            self.schema.execute(Path('db/init/06_audit.sql'))
            self.load_to_pg(Path("data/raw/raw_yellow_tripdata_2026_01.parquet"), "raw_taxi_trips", Layer.BRONZE)
            self.load_to_pg(Path("data/raw/taxi_zone_lookup.csv"), "raw_taxi_lookup", Layer.BRONZE)
            
            rows = self.schema.fetch(
                """
                SELECT COUNT(*)
                FROM bronze.raw_taxi_trips
                """
            )
            
            self.audit.log_pipeline(
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
            
            self.conn.rollback()
            
            self.audit.log_pipeline(
                layer="bronze",
                process_name="load to bronze",
                start_time=start,
                end_time=datetime.now(),
                rows_processed=0,
                status="FAILED",
                message=f"[ERROR] {str(e)}"
            )
            
            raise