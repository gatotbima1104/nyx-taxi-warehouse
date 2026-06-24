from scripts.extractor import TaxiExtractor
from utils.constants import (
    TAXI_DATA_FILENAME,
    TAXI_DATA_URL,
    TAXI_ZONE_LOOKUP_TABLE,
    TAXI_ZONE_LOOKUP_URL
)

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

if __name__ == '__main__':
    extract()