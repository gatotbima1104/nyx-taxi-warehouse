from datetime import datetime
from utils.helpers import Helper

from scripts.configs import SILVER_SQL_FILES, SILVER_OUTPUTS

from scripts.managers import (
    SchemaManager,
    AuditManager
)

class SilverTransformer:
    def __init__(self, conn, start_period, end_period):
        self.conn = conn
        self.start_period = start_period
        self.end_period = end_period
        self.schema = SchemaManager(conn)
        self.audit = AuditManager(conn)
        
    def transform(self):
        start = datetime.now()
        
        try:
            self.schema.execute_many(
                SILVER_SQL_FILES,
                params={
                    "start_period": self.start_period,
                    "end_period": self.end_period
                })
            self._log_outputs(start)
            
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
    
    def _log_outputs(self, start_time):

        for output in SILVER_OUTPUTS:
            rows = self.schema.count(output["table"])
            
            print(f'[LOAD TO SILVER] Loaded {rows:,} rows into {output["table"]}')
            
            self.audit.log_pipeline(
                layer="silver",
                process_name=output["process"],
                start_time=start_time,
                end_time=datetime.now(),
                rows_processed=rows,
                status="SUCCESS",
                message=output["message"]
            )