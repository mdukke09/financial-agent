from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

from config.settings import MONGODB_URI, MONGODB_DATABASE

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

# Collection para tokens en la lista negra
TokenBlacklist = db['token_blacklist']

# Crear índices
TokenBlacklist.create_index([("jti", 1)], unique=True)
TokenBlacklist.create_index([("expires_at", 1)], expireAfterSeconds=0)  # TTL index para auto-eliminación


def add_token_to_blacklist(jti, expires_delta):
    """
    Añade un token a la lista negra
    
    Args:
        jti (str): Identificador único del token (JWT ID)
        expires_delta (int): Tiempo en segundos hasta que expira
    """
    expires_at = datetime.now() + timedelta(seconds=expires_delta)
    
    # Guardar token en lista negra
    TokenBlacklist.insert_one({
        "jti": jti,
        "created_at": datetime.now(),
        "expires_at": expires_at
    })


def is_token_blacklisted(jti):
    """
    Verifica si un token está en la lista negra
    
    Args:
        jti (str): Identificador único del token (JWT ID)
    
    Returns:
        bool: True si el token está en la lista negra
    """
    return TokenBlacklist.find_one({"jti": jti}) is not None


def prune_expired_tokens():
    """
    Elimina tokens expirados de la lista negra
    
    Nota: MongoDB eliminará automáticamente los documentos expirados, 
    pero esta función se puede usar para limpiar manualmente si es necesario.
    """
    TokenBlacklist.delete_many({"expires_at": {"$lt": datetime.now()}})