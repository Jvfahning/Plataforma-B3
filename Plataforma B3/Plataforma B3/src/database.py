from azure.cosmos import CosmosClient, exceptions, PartitionKey
from typing import Generator
from config import settings

# Configuração do CosmosDB
client = CosmosClient(settings.COSMOSDB_URL, credential=settings.COSMOSDB_KEY)
database = client.create_database_if_not_exists(id=settings.COSMOSDB_DB)
container = database.create_container_if_not_exists(
    id=settings.COSMOSDB_CONTAINER,
    partition_key=PartitionKey(path="/partitionKey"),
    offer_throughput=400
)

def get_db() -> Generator:
    """Retorna uma sessão do banco de dados"""
    try:
        yield container
    finally:
        pass  # O CosmosDB gerencia suas próprias conexões