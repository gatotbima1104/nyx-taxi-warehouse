from scripts.taxi_extractor import TaxiExtractor
from scripts.database_connection import DatabaseConnection
from scripts.reporters import PipelineReporter

from scripts.layers.bronze import BronzeLoader
from scripts.layers.silver import SilverTransformer
from scripts.layers.gold import (
    GoldMartBuilder,
    ViewCreator,
    QueryRunner
)

from utils.helpers import Helper
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
    BronzeLoader(conn).load_to_bronze()
 
def transform_to_silver():
    start_period, end_period = Helper.get_dataset_period(TAXI_DATA_FILENAME)
    SilverTransformer(conn, start_period, end_period).transform()

def analytics_to_gold():
    GoldMartBuilder(conn).build()

def create_views():
    ViewCreator(conn).create()
    
def analytics():
    QueryRunner(conn).run()
    
def report():
    PipelineReporter(conn).generate()

if __name__ == '__main__':
    extract()
    load_to_bronze()
    transform_to_silver()
    analytics_to_gold()
    create_views()
    analytics()
    report()