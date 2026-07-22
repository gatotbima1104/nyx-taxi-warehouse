from pathlib import Path
from utils.constants import TAXI_DATA_FILENAME

# BRONZE
BRONZE_SQL_FILES = [
    Path('db/init/01_schema.sql'),
    Path('db/init/02_bronze_load.sql'),
    Path('db/init/06_audit.sql')
]

BRONZE_LOADS = [
    {
        "file": Path(f"data/raw/{TAXI_DATA_FILENAME}"),
        "table": "raw_taxi_trips",
    },
    {
        "file": Path("data/raw/taxi_zone_lookup.csv"),
        "table": "raw_taxi_lookup",
    },
]


# SILVER
SILVER_SQL_FILES = [
    Path('db/init/03_silver_transform.sql'),
    *sorted(Path('db/schemas/silver').glob('*.sql'))
]

SILVER_OUTPUTS = [
    {
        "table": "silver.taxi_trips_cleaned",
        "process": "load valid data to silver",
        "message": "[SILVER] Valid data loaded successfully."
    },
    {
        "table": "silver.data_quality_issues",
        "process": "load invalid data to silver",
        "message": "[SILVER] Invalid data loaded successfully."
    }
]

# GOLD
GOLD_SQL_FILES = [
    Path('db/init/04_gold_mart.sql'),
    *sorted(Path('db/schemas/gold').glob('*.sql'))
]

GOLD_VIEW_CREATOR_FILE = Path('db/init/05_views.sql')
GOLD_QUERY_RUNNER_FILE = sorted(Path("db/queries").glob("*.sql"))


# REPORT
BUSINESS_ANALYTICS_LOG_PATH = "logs/business_analytics.log"