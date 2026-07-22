import time
import pandas as pd
import re
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Callable
from pandas import DataFrame
from datetime import datetime

class Helper:
    LOADERS = {
        '.csv' : pd.read_csv,
        '.xlsx' : pd.read_excel,
        '.parquet': pd.read_parquet,
        '.json': pd.read_json
    }
    
    @staticmethod
    def create_dir(output_path: Path | str) -> Path:
        """ Make a directory with pathlib """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path.parent
    
    @staticmethod
    def load_file(filepath: Path) -> DataFrame:
        """ Load file """
        suffix = filepath.suffix.lower() # .csv | .xlsx | etc.
        if suffix not in Helper.LOADERS:
            raise ValueError(
                f"Unsopported file format: {suffix}"
            )
            
        print(f'[LOAD] Loading {suffix} data ...')
        return Helper.LOADERS[suffix](filepath) # pd.read_csv(filepath)
        
    @staticmethod
    def save_to_csv(dataframe: DataFrame, output_path: Path) -> None:
        """ save file """
        Helper.create_dir(output_path)
        dataframe.to_csv(output_path, index=False)
        
    @staticmethod
    def log(message: str, isShowTimestamp: bool = True) -> str:
        """logging information"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isShowTimestamp:
            print(f"[INFO] {timestamp} - {message}", flush=True)
        else:
            print(f"[INFO] {message}", flush=True)

    @staticmethod
    def measure(step_name: str, func: Callable):
        """measure time performance"""
        Helper.log(f"{step_name} ...")

        start = time.perf_counter()
        result = func()
        duration = time.perf_counter() - start

        Helper.log(f"{step_name} completed in {duration:.2f}s")
        return result
    
    @staticmethod
    def generate_report(valid_data: DataFrame, invalid_data: DataFrame, stats: dict, execution_time: float) -> None:
        """reporting dataset information"""
        total_rows = len(valid_data) + len(invalid_data)

        valid_pct = (
            len(valid_data) / total_rows * 100
            if total_rows else 0
        )

        invalid_pct = (
            len(invalid_data) / total_rows * 100
            if total_rows else 0
        )
    
        time.sleep(1)
        
        Helper.log("", isShowTimestamp=False)
        Helper.log("DATA QUALITY REPORT", isShowTimestamp=False)
        Helper.log("", isShowTimestamp=False)

        Helper.log("Dataset Summary", isShowTimestamp=False)
        Helper.log("-" * 15, isShowTimestamp=False)
        Helper.log(f"Total Records      : {total_rows:,}", isShowTimestamp=False)
        Helper.log(f"Valid Records      : {len(valid_data):,} ({valid_pct:.2f}%)", isShowTimestamp=False)
        Helper.log(f"Invalid Records    : {len(invalid_data):,} ({invalid_pct:.2f}%)", isShowTimestamp=False)

        Helper.log("", isShowTimestamp=False)
        Helper.log("Invalid Record Breakdown", isShowTimestamp=False)
        Helper.log("-" * 24, isShowTimestamp=False)
        Helper.log(f"Duration Invalid   : {stats['invalid_duration']:,}", isShowTimestamp=False)
        Helper.log(f"Distance Invalid   : {stats['invalid_distance']:,}", isShowTimestamp=False)

        Helper.log("", isShowTimestamp=False)
        Helper.log("Pipeline", isShowTimestamp=False)
        Helper.log("-" * 8, isShowTimestamp=False)
        Helper.log(f"Execution Time     : {execution_time:.2f}s", isShowTimestamp=False)
        Helper.log("", isShowTimestamp=False)

        Helper.log("=" * 50, isShowTimestamp=False)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_records": int(total_rows),
            "valid_records": len(valid_data),
            "invalid_records": {
                "total": len(invalid_data),
                "invalid_duration": stats['invalid_duration'],
                "invalid_distance": stats['invalid_distance']
            },
            "execution_time_seconds": round(execution_time, 2)
        }
    
    @staticmethod
    def get_dataset_period(filename: str) -> tuple[datetime, datetime]:
        """
            Example: yellow_tripdata_2026-01.parquet
            Returns:(datetime(2026,1,1), datetime(2026,2,1))
        """
        match = re.search(r"(\d{4})-(\d{2})", filename)

        if not match:
            raise ValueError(
                f"Cannot determine dataset period from '{filename}'"
            )

        year = int(match.group(1))
        month = int(match.group(2))

        start = datetime(year, month, 1)
        end = start + relativedelta(months=1)

        return start, end
        