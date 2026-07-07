from scripts.managers import SchemaManager
from pathlib import Path
from utils.helpers import Helper

class ViewCreator:
    def __init__(self, conn):
        self.conn = conn
        self.schema = SchemaManager(conn)
        
    def create(self):
        self.schema.execute(Path('db/init/05_views.sql'))
        Helper.log(message="Views created successfully ... ")