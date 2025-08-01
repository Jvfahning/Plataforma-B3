from pymongo import MongoClient
from typing import Generator
from config import settings

client = MongoClient(settings.COSMOSDB_URL)

db = client['plataforma_B3']

def get_db() -> Generator:
    
    try:
        yield db['flows']
    finally:
        pass