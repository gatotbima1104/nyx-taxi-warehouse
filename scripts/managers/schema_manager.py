from pathlib import Path
from psycopg2.extensions import connection as PGConnection

class SchemaManager():
    def __init__(self, connection: PGConnection):
        self.connection = connection
        
    @staticmethod
    def read(filepath: Path) -> str:
        with open(filepath, 'r', encoding="utf-8") as f:
            return f.read()
        
    def execute(self, filepath: Path) -> None:
        sql = self.read(filepath)
        with self.connection.cursor() as cur:
            cur.execute(sql)
        
        self.connection.commit()
        print(f'[SCHEMA] Executed {filepath.name}')
        
    def execute_many(self, filepath: list[Path], params=None) -> None:
        print("params", params)
        with self.connection.cursor() as cur:
            for filepath in filepath:
                sql = self.read(filepath)
                cur.execute(sql, params)
                print(f'[SQL] Executed {filepath.name}')
        
        self.connection.commit()

    def fetch(self, sql: str):
        with self.connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()[0]
        
    def count(self, table):
        return self.fetch(f"SELECT COUNT(*) FROM {table}")

    def report(self, filepath: Path) -> int:
        sql = self.read(filepath)
        
        if not sql:
             print(f"[SKIP] {filepath.name} (empty file)")
             return 0

        with self.connection.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

        print("\n" + "=" * 80)
        print(f"[BUSINESS QUERY] {filepath.stem}")
        print("=" * 80)

        print(" | ".join(columns))
        print("-" * 80)

        for row in rows[:10]:
            print(" | ".join(str(v) for v in row))

        if len(rows) > 10:
            print(f"... ({len(rows) - 10} more rows)")

        print(f"\nReturned {len(rows)} rows\n")

        return len(rows)
    
    def report_many(self, filepaths: list[Path]) -> int:
        total_rows = 0

        for filepath in filepaths:
            total_rows += self.report(filepath)

        return total_rows