from datetime import datetime
from pathlib import Path
from utils.helpers import Helper
from contextlib import redirect_stdout

from scripts.managers import (
    SchemaManager,
    AuditManager
)

class QueryRunner:
    def __init__(self, conn):
        self.conn = conn
        self.schema = SchemaManager(conn)
        self.audit = AuditManager(conn)
    
    def run(self):
        start = datetime.now()

        try:
            queries = sorted(Path("db/queries").glob("*.sql"))
            
            with open("logs/business_analytics.log", "w", encoding="utf-8") as log:
                with redirect_stdout(log):
                    self.schema.report_many(queries)

            self.audit.log_pipeline(
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

            self.conn.rollback()

            self.audit.log_pipeline(
                layer="gold",
                process_name="business analytics",
                start_time=start,
                end_time=datetime.now(),
                rows_processed=0,
                status="FAILED",
                message=str(e)
            )

            raise