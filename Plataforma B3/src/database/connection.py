import os
from azure.cosmos import CosmosClient, PartitionKey, IndexingPolicy
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações do Cosmos DB
COSMOS_ENDPOINT = os.getenv("AZURE_COSMOS_ENDPOINT", "https://localhost:8081")
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY", "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")
DATABASE_NAME = os.getenv("AZURE_COSMOS_DATABASE", "b3_platform")

# Inicialização do cliente
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.create_database_if_not_exists(id=DATABASE_NAME)

# Configuração dos containers
containers = {
    "users": {
        "partition_key": PartitionKey(path="/id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    },
    "workflows": {
        "partition_key": PartitionKey(path="/user_id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    },
    "themes": {
        "partition_key": PartitionKey(path="/id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    },
    "chats": {
        "partition_key": PartitionKey(path="/user_id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    },
    "documents": {
        "partition_key": PartitionKey(path="/user_id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    },
    "goals": {
        "partition_key": PartitionKey(path="/user_id"),
        "indexing_policy": IndexingPolicy(
            automatic=True,
            indexing_mode="consistent"
        )
    }
}

# Criação dos containers
for container_name, container_config in containers.items():
    try:
        database.create_container(
            id=container_name,
            partition_key=container_config["partition_key"],
            indexing_policy=container_config["indexing_policy"]
        )
    except Exception as e:
        if "Recurso com o ID, nome ou índice único especificado já existe" not in str(e):
            raise e

def get_container(container_name: str):
    """
    Obtém uma referência para um container.
    
    Args:
        container_name: Nome do container
        
    Returns:
        Referência para o container
    """
    return database.get_container_client(container_name)

def get_database():
    """
    Obtém uma referência para o banco de dados.
    
    Returns:
        Referência para o banco de dados
    """
    return database

def get_client():
    """
    Obtém uma referência para o cliente.
    
    Returns:
        Referência para o cliente
    """
    return client

def close_connection():
    """
    Fecha a conexão com o banco de dados.
    """
    client.close() 