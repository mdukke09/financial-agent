from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

from config.settings import MONGODB_URI, MONGODB_DATABASE

# Inicializar cliente de MongoDB Atlas
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

# Colecciones
FinancialGoal = db['financial_goals']
Conversation = db['conversations']

# Create indexes
FinancialGoal.create_index([("user_id", 1)])
FinancialGoal.create_index([("session_id", 1)])
FinancialGoal.create_index([("categoria", 1)])
FinancialGoal.create_index([("estado", 1)])
FinancialGoal.create_index([("nombre", "text"), ("descripcion", "text")])

Conversation.create_index([("session_id", 1), ("user_id", 1)], unique=True)
Conversation.create_index([("updated_at", -1)])


class FinancialGoalModel:
    """Class representing a financial goal"""
    
    def __init__(self, nombre, valor, tiempo, descripcion, session_id, user_id, 
                 fecha_creacion=None, categoria=None, estado="pendiente", _id=None):
        self.nombre = nombre
        self.valor = valor
        self.tiempo = tiempo
        self.descripcion = descripcion
        self.session_id = session_id
        self.user_id = user_id
        self.fecha_creacion = fecha_creacion or datetime.now().isoformat()
        self.categoria = categoria
        self.estado = estado
        self._id = _id
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        if '_id' in data:
            data['_id'] = ObjectId(data['_id']) if isinstance(data['_id'], str) else data['_id']
        return cls(**data)
    
    def to_dict(self):
        """Convert instance to dictionary"""
        result = {
            "nombre": self.nombre,
            "valor": self.valor,
            "tiempo": self.tiempo,
            "descripcion": self.descripcion,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "fecha_creacion": self.fecha_creacion,
            "estado": self.estado
        }
        
        if self.categoria:
            result["categoria"] = self.categoria
            
        if self._id:
            result["_id"] = str(self._id)
            
        return result
    
    def save(self):
        """Save model to database"""
        data = self.to_dict()
        if '_id' in data:
            _id = data.pop('_id')
            FinancialGoal.update_one({"_id": ObjectId(_id)}, {"$set": data})
            return _id
        else:
            result = FinancialGoal.insert_one(data)
            self._id = result.inserted_id
            return result.inserted_id


class ConversationModel:
    """Class representing a conversation"""
    
    def __init__(self, session_id, user_id, messages=None, created_at=None, updated_at=None, _id=None):
        self.session_id = session_id
        self.user_id = user_id
        self.messages = messages or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self._id = _id
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        if '_id' in data:
            data['_id'] = ObjectId(data['_id']) if isinstance(data['_id'], str) else data['_id']
        return cls(**data)
    
    def to_dict(self):
        """Convert instance to dictionary"""
        result = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
            
        if self._id:
            result["_id"] = str(self._id)
            
        return result
    
    def add_message(self, role, content):
        """Add a message to conversation"""
        now = datetime.now()
        message = {
            "role": role,
            "content": content,
            "timestamp": now
        }
        self.messages.append(message)
        self.updated_at = now
        
        # Update in database if _id exists
        if self._id:
            Conversation.update_one(
                {"_id": self._id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": now}
                }
            )
    
    def save(self):
        """Save model to database"""
        data = self.to_dict()
        if '_id' in data:
            _id = data.pop('_id')
            Conversation.update_one({"_id": ObjectId(_id)}, {"$set": data})
            return _id
        else:
            result = Conversation.insert_one(data)
            self._id = result.inserted_id
            return result.inserted_id