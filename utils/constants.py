from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST") or "localhost"
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT")) or 5432
POSTGRES_DB = os.getenv("POSTGRES_DB") or ""
POSTGRES_USER = os.getenv("POSTGRES_USER") or "postgres"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") or "postgres"
POSTGRES_URL = os.getenv("POSTGRES_URL") or ""

TAXI_URL = os.getenv("TAXI_URL") or "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
TAXI_ZONE_LOOKUP_URL = os.getenv("TAXI_ZONE_LOOKUP_URL") or "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
TAXI_DATA_FILENAME = os.getenv("TAXI_DATA_FILENAME") or "raw_yellow_tripdata_2026_01.parquet"
TAXI_ZONE_LOOKUP_TABLE = os.getenv("TAXI_ZONE_LOOKUP_TABLE") or "taxi_zone_lookup.csv"
CHUNK_SIZE = 8192