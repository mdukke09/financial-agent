from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

from config.settings import MONGODB_URI, MONGODB_DATABASE

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

# Collections
User = db['users']

# Create indexes
User.create_index([("email", 1)], unique=True)
User.create_index([("role", 1)])


class UserModel:
    """Class representing a user"""
    
    def __init__(self, name, email, password_hash=None, role="user", 
                 active=True, created_at=None, updated_at=None, last_login=None, _id=None):
        self.name = name
        self.email = email.lower()
        self.password_hash = password_hash
        self.role = role
        self.active = active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.last_login = last_login
        self._id = _id
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        if '_id' in data:
            data['_id'] = ObjectId(data['_id']) if isinstance(data['_id'], str) else data['_id']
        return cls(**data)
    
    def to_dict(self, include_password=False):
        """Convert instance to dictionary"""
        result = {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login
        }
        
        if include_password and self.password_hash:
            result["password_hash"] = self.password_hash
            
        if self._id:
            result["_id"] = str(self._id)
            
        return result
    
    def save(self):
        """Save model to database"""
        data = self.to_dict(include_password=True)
        if '_id' in data:
            _id = data.pop('_id')
            User.update_one({"_id": ObjectId(_id)}, {"$set": data})
            return _id
        else:
            result = User.insert_one(data)
            self._id = result.inserted_id
            return result.inserted_id
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        user_data = User.find_one({"email": email.lower()})
        if user_data:
            return cls.from_dict(user_data)
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = User.find_one({"_id": user_id})
        if user_data:
            return cls.from_dict(user_data)
        return None