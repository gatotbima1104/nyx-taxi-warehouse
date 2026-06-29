from pathlib import Path
from scripts.extractor import TaxiExtractor
from utils.constants import (
    TAXI_DATA_FILENAME,
    TAXI_DATA_URL,
    TAXI_ZONE_LOOKUP_TABLE,
    TAXI_ZONE_LOOKUP_URL,
    POSTGRES_URL,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER
)
from scripts.database import DatabaseConnection
from scripts.loader import BronzeLoader
from scripts.schema_manager import SchemaManager
from scripts.loader import Layer

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

def extract() -> list[str]:
    extract_files = [
        (TAXI_DATA_URL, TAXI_DATA_FILENAME),
        (TAXI_ZONE_LOOKUP_URL, TAXI_ZONE_LOOKUP_TABLE)
    ]

    extractor = TaxiExtractor()
    downloaded_files = []

    for url, filename in extract_files:
        downloaded_files.append(
            extractor.extract(url, filename)
        )
    
    return downloaded_files

def load_to_bronze():
    # L1 --> BRONZE LAYER
    loader = BronzeLoader(conn)
    
    schema.execute(Path('db/init/01_schema.sql'))
    schema.execute(Path('db/init/02_bronze_load.sql'))
    loader.load_data(Path("data/raw/raw_yellow_tripdata_2026_01.parquet"), "raw_taxi_trips", Layer.BRONZE)
    loader.load_data(Path("data/raw/taxi_zone_lookup.csv"), "raw_taxi_lookup", Layer.BRONZE)
    
def transform_to_silver():
    # L2 --> SILVER LAYER
    silver_layer = [
        Path('db/init/03_silver_transform.sql'),
        *sorted(Path('db/schemas/silver').glob('*.sql'))
    ]
    schema.execute_many(silver_layer)
    print(f'[LOAD TO SILVER] Loaded {schema.fetch("SELECT COUNT(*) FROM silver.taxi_trips_cleaned"):,} valid rows ...')
    print(f'[LOAD TO SILVER] Loaded {schema.fetch("SELECT COUNT(*) FROM silver.data_quality_issues"):,} invalid rows ...')
    
def analytics_to_gold():
    # L3 --> GOLD LAYER
    gold_layer = [
        Path('db/init/04_gold_mart.sql'),
        *sorted(Path('db/schemas/gold').glob('*.sql'))
    ]
    schema.execute_many(gold_layer)

if __name__ == '__main__':
    extract()
    load_to_bronze()
    transform_to_silver()
    analytics_to_gold()