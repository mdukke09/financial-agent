import logging
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from bson.objectid import ObjectId

# from config.settings import JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES
from models.users import User

logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio para gestionar la autenticación y tokens
    """
    
    @staticmethod
    def login(email, password):
        """
        Autentica a un usuario y genera tokens JWT
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Buscar usuario por email
            user = User.find_one({"email": email.lower()})
            
            if not user:
                return {"success": False, "message": "Usuario no encontrado"}, 404
            
            # Verificar contraseña
            if not AuthService._verify_password(password, user.get('password_hash', '')):
                return {"success": False, "message": "Credenciales inválidas"}, 401
            
            # Generar tokens
            access_token, refresh_token = AuthService._generate_tokens(str(user['_id']))
            
            # Actualizar último acceso
            User.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.now()}}
            )
            
            # Preparar respuesta
            return {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": str(user['_id']),
                        "name": user.get('name', ''),
                        "email": user.get('email', ''),
                        "role": user.get('role', 'user')
                    }
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def register(user_data):
        """
        Registra un nuevo usuario
        
        Args:
            user_data (dict): Datos del usuario
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            email = user_data.get('email', '').lower()
            
            # Verificar si el email ya está registrado
            existing_user = User.find_one({"email": email})
            if existing_user:
                return {"success": False, "message": "El email ya está registrado"}, 400
            
            # Crear hash de la contraseña
            password_hash = AuthService._hash_password(user_data.get('password', ''))
            
            # Preparar datos del usuario
            new_user = {
                "name": user_data.get('name', ''),
                "email": email,
                "password_hash": password_hash,
                "role": user_data.get('role', 'user'),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "last_login": None,
                "active": True
            }
            
            # Insertar usuario en la base de datos
            result = User.insert_one(new_user)
            
            # Generar tokens
            access_token, refresh_token = AuthService._generate_tokens(str(result.inserted_id))
            
            return {
                "success": True,
                "message": "Usuario registrado exitosamente",
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": str(result.inserted_id),
                        "name": new_user.get('name', ''),
                        "email": new_user.get('email', ''),
                        "role": new_user.get('role', 'user')
                    }
                }
            }, 201
            
        except Exception as e:
            logger.error(f"Error en register: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def refresh_token(refresh_token):
        """
        Refresca el token de acceso usando un token de refresco
        
        Args:
            refresh_token (str): Token de refresco
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Obtener identidad del usuario desde el token
            user_id = get_jwt_identity()
            
            if not user_id:
                return {"success": False, "message": "Token inválido"}, 401
            
            # Verificar que el usuario existe
            user = User.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return {"success": False, "message": "Usuario no encontrado"}, 404
            
            # Generar nuevo token de acceso
            access_token = create_access_token(identity=user_id)
            
            return {
                "success": True,
                "message": "Token refrescado exitosamente",
                "data": {
                    "access_token": access_token
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error en refresh_token: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def _generate_tokens(user_id):
        """
        Genera tokens JWT para un usuario
        
        Args:
            user_id (str): ID del usuario
            
        Returns:
            tuple: (access_token, refresh_token)
        """
        # Token de acceso (corta duración)
        access_token = create_access_token(identity=user_id)
        
        # Token de refresco (larga duración)
        refresh_token = create_refresh_token(identity=user_id)
        
        return access_token, refresh_token
    
    @staticmethod
    def _hash_password(password):
        """
        Crea un hash seguro de la contraseña
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        import bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(password, password_hash):
        """
        Verifica si una contraseña coincide con su hash
        
        Args:
            password (str): Contraseña en texto plano
            password_hash (str): Hash almacenado
            
        Returns:
            bool: True si la contraseña coincide
        """
        import bcrypt
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)