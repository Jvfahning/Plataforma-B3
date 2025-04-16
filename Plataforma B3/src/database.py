from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import AsyncGenerator, Generator
from config import settings

# Cliente síncrono para operações que não precisam ser assíncronas
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB]
collection = db[settings.MONGODB_COLLECTION]

# Cliente assíncrono para operações assíncronas
async_client = AsyncIOMotorClient(settings.MONGODB_URL)
async_db = async_client[settings.MONGODB_DB]
async_collection = async_db[settings.MONGODB_COLLECTION]

def get_db() -> Generator:
    """Retorna uma sessão do banco de dados síncrona"""
    try:
        yield collection
    finally:
        pass  # O MongoDB gerencia suas próprias conexões

async def get_async_db() -> AsyncGenerator:
    """Retorna uma sessão do banco de dados assíncrona"""
    try:
        yield async_collection
    finally:
        pass  # O MongoDB gerencia suas próprias conexões 