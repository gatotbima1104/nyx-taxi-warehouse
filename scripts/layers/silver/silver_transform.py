from datetime import datetime
from pathlib import Path
from utils.helpers import Helper

from scripts.managers import (
    SchemaManager,
    AuditManager
)

class SilverTransformer:
    def __init__(self, conn):
        self.conn = conn
        self.schema = SchemaManager(conn)
        self.audit = AuditManager(conn)
        
    def transform(self):
        start = datetime.now()
        
        try:
            silver_layer = [
                Path('db/init/03_silver_transform.sql'),
                *sorted(Path('db/schemas/silver').glob('*.sql'))
            ]
            self.schema.execute_many(silver_layer)
            
            rows_taxi_cleaned = self.schema.fetch(
                """
                SELECT COUNT(*) 
                FROM silver.taxi_trips_cleaned
                """
            )
            
            rows_data_quality_issues = self.schema.fetch(
                """
                SELECT COUNT(*) 
                FROM silver.data_quality_issues
                """
            )
            
            print(f'[LOAD TO SILVER] Loaded {rows_taxi_cleaned:,} valid rows ...')
            print(f'[LOAD TO SILVER] Loaded {rows_data_quality_issues:,} invalid rows ...')
            
            self.audit.log_pipeline(
                layer="silver",
                process_name="load valid data to silver",
                start_time=start,
                end_time=datetime.now(),
                rows_processed=rows_taxi_cleaned,
                status="SUCCESS",
                message="[SILVER] Valid data loaded successfully."
            )
            
            self.audit.log_pipeline(
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
            self.conn.rollback()
            self.audit.log_pipeline(
                layer="silver",
                process_name="silver transform",
                start_time=start,
                end_time=datetime.now(),
                rows_processed=0,
                status="FAILED",
                message=f"[ERROR] {str(e)}"
            )
            
            raise