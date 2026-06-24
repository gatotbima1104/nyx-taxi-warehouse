import requests
from tqdm import tqdm
from utils.constants import CHUNK_SIZE
from pathlib import Path
from abc import ABC, abstractmethod
from utils.helpers import Helper

class Exract(ABC):
    @abstractmethod
    def extract(self):
        pass

class TaxiExtractor(Exract):
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def download_file(self, url: str, output_path: Path) -> Path:
        """ Download file using requests """
        try:            
            Helper.create_dir(output_path) # Make a dir from helper
            
            if output_path.exists():
                print(f"✓ File already exists: {output_path}")
                return output_path
            
            with requests.get(url=url, stream=True, timeout=30) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                
                with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as progress_bar:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                progress_bar.update(len(chunk))
            
            print("Completed ... \n")
            return output_path
        
        except requests.RequestException as error:
            print(f"Download failed: {error}")
            raise
    
    def extract(self, url: str, filename: str) -> Path:  
        """ Ingesting data from downloaded file """
        print(f"[EXTRACT] {filename}")
        output_path = (self.base_dir / ".." / "data" / "raw" / filename)
        return self.download_file(url, output_path)