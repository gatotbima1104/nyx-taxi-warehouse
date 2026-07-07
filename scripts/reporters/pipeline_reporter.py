class PipelineReporter:
    def __init__(self, conn):
        self.conn = conn
        
    def generate(self):
        print("\n")
        print("=" * 80)
        print("                     NYC TAXI PIPELINE EXECUTION REPORT")
        print("=" * 80)

        with self.conn.cursor() as cur:

            # Summary setiap proses
            cur.execute("""
                SELECT
                    layer,
                    process_name,
                    start_time,
                    end_time,
                    rows_processed,
                    status,
                    EXTRACT(EPOCH FROM (end_time - start_time)) AS duration
                FROM audit.logs
                ORDER BY run_id;
            """)

            logs = cur.fetchall()

            pipeline_start = logs[0][2]
            pipeline_end = logs[-1][3]
            total_duration = pipeline_end - pipeline_start

            print(f"Started  : {pipeline_start}")
            print(f"Finished : {pipeline_end}")
            print(f"Duration : {total_duration}")

            print("\n" + "-" * 80)
            print(
                f'{"Layer":<10}'
                f'{"Process":<30}'
                f'{"Rows":>15}'
                f'{"Time(s)":>12}'
                f'{"Status":>12}'
            )
            print("-" * 80)

            for layer, process, _, _, rows, status, duration in logs:
                rows = "-" if rows is None else f"{rows:,}"

                print(
                    f"{layer:<10}"
                    f"{process:<30}"
                    f"{rows:>15}"
                    f"{duration:>12.2f}"
                    f"{status:>12}"
                )

            # Data quality
            cur.execute(
                """
                SELECT COUNT(*)
                FROM bronze.raw_taxi_trips
                """
            )
            raw = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM silver.taxi_trips_cleaned
                """
            )
            valid = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM silver.data_quality_issues
                """
            )
            invalid = cur.fetchone()[0]

            cur.execute("""
                SELECT
                    error_type,
                    COUNT(*)
                FROM silver.data_quality_issues
                GROUP BY error_type
                ORDER BY COUNT(*) DESC;
            """)
            reasons = cur.fetchall()

        print("\n" + "-" * 80)
        print("DATA QUALITY")
        print("-" * 80)

        print(f"Raw Records     : {raw:,}")
        print(f"Valid Records   : {valid:,}")
        print(f"Invalid Records : {invalid:,}")

        print("\nInvalid Reasons")

        for reason, total in reasons:
            print(f"  • {reason:<30} {total:,}")

        print("\n" + "=" * 80)
        print("Pipeline Status : SUCCESS")
        print("=" * 80)