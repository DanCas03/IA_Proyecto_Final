"""
Módulo de conexión a MongoDB Atlas.
Gestiona la conexión, creación de base de datos y colecciones.
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "textos_clasicos")

# Colecciones del proyecto
COLLECTIONS = {
    "raw_texts": "raw_texts",           # Datos crudos extraídos de Excel
    "processed_texts": "processed_texts", # Datos preprocesados y balanceados
    "train_data": "train_data",         # Conjunto de entrenamiento
    "val_data": "val_data",             # Conjunto de validación
    "test_data": "test_data",           # Conjunto de prueba
}

_client: MongoClient = None


def get_client() -> MongoClient:
    """Obtiene o crea la conexión al cliente de MongoDB."""
    global _client
    if _client is None:
        if not MONGO_URI:
            raise ValueError(
                "MONGO_URI no está configurado. "
                "Crea un archivo .env con tu cadena de conexión."
            )
        _client = MongoClient(MONGO_URI)
    return _client


def get_database() -> Database:
    """Obtiene la base de datos del proyecto."""
    client = get_client()
    return client[DB_NAME]


def get_collection(collection_name: str) -> Collection:
    """
    Obtiene una colección específica.
    
    Args:
        collection_name: Nombre de la colección (usar claves de COLLECTIONS)
    
    Returns:
        Collection de MongoDB
    """
    db = get_database()
    return db[COLLECTIONS.get(collection_name, collection_name)]


def init_database() -> dict:
    """
    Inicializa la base de datos y las colecciones necesarias.
    
    Returns:
        Diccionario con información de la inicialización
    """
    db = get_database()
    existing_collections = db.list_collection_names()
    created = []
    
    for collection_key, collection_name in COLLECTIONS.items():
        if collection_name not in existing_collections:
            db.create_collection(collection_name)
            created.append(collection_name)
    
    return {
        "database": DB_NAME,
        "existing_collections": existing_collections,
        "created_collections": created,
        "all_collections": list(COLLECTIONS.values())
    }


def test_connection() -> bool:
    """
    Prueba la conexión a MongoDB Atlas.
    
    Returns:
        True si la conexión es exitosa
    """
    try:
        client = get_client()
        # Ping para verificar conexión
        client.admin.command('ping')
        print(f"✓ Conexión exitosa a MongoDB Atlas")
        print(f"✓ Base de datos: {DB_NAME}")
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False


def clear_collection(collection_name: str) -> int:
    """
    Limpia todos los documentos de una colección.
    
    Args:
        collection_name: Nombre de la colección
    
    Returns:
        Número de documentos eliminados
    """
    collection = get_collection(collection_name)
    result = collection.delete_many({})
    return result.deleted_count


if __name__ == "__main__":
    # Test de conexión
    if test_connection():
        info = init_database()
        print(f"\n📊 Información de la base de datos:")
        print(f"   Base de datos: {info['database']}")
        print(f"   Colecciones existentes: {info['existing_collections']}")
        print(f"   Colecciones creadas: {info['created_collections']}")
