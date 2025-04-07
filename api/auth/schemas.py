from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """Esquema para iniciar sesión"""
    email = fields.Email(required=True, description="Correo electrónico del usuario")
    password = fields.String(required=True, description="Contraseña del usuario")


class UserDataSchema(Schema):
    """Esquema para datos de usuario"""
    id = fields.String(required=True, description="ID único del usuario")
    name = fields.String(required=True, description="Nombre del usuario")
    email = fields.Email(required=True, description="Correo electrónico del usuario")
    role = fields.String(required=True, description="Rol del usuario", default="user")


class TokensDataSchema(Schema):
    """Esquema para datos de tokens"""
    access_token = fields.String(required=True, description="Token de acceso JWT")
    refresh_token = fields.String(required=False, description="Token de refresco JWT")
    user = fields.Nested(UserDataSchema, required=True, description="Datos del usuario")


class LoginResponseDataSchema(Schema):
    """Esquema para datos de respuesta al iniciar sesión"""
    data = fields.Nested(TokensDataSchema, required=True, description="Datos de tokens y usuario")


class LoginResponseSchema(Schema):
    """Esquema para respuesta al iniciar sesión"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=True)
    message = fields.String(required=True, description="Mensaje de respuesta", example="Inicio de sesión exitoso")
    data = fields.Nested(TokensDataSchema, required=False, description="Datos de tokens y usuario")


class RegisterSchema(Schema):
    """Esquema para registrar usuario"""
    name = fields.String(required=True, description="Nombre del usuario", 
                         validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, description="Correo electrónico del usuario")
    password = fields.String(required=True, description="Contraseña del usuario", 
                             validate=validate.Length(min=6))
    role = fields.String(required=False, description="Rol del usuario", 
                         validate=validate.OneOf(["user", "admin"]), default="user")


class RegisterResponseSchema(Schema):
    """Esquema para respuesta al registrar usuario"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=True)
    message = fields.String(required=True, description="Mensaje de respuesta", example="Usuario registrado exitosamente")
    data = fields.Nested(TokensDataSchema, required=False, description="Datos de tokens y usuario")


class RefreshTokenSchema(Schema):
    """Esquema para refrescar token"""
    refresh_token = fields.String(required=True, description="Token de refresco JWT")


class RefreshTokenResponseDataSchema(Schema):
    """Esquema para datos de respuesta al refrescar token"""
    access_token = fields.String(required=True, description="Nuevo token de acceso JWT")


class RefreshTokenResponseSchema(Schema):
    """Esquema para respuesta al refrescar token"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=True)
    message = fields.String(required=True, description="Mensaje de respuesta", example="Token refrescado exitosamente")
    data = fields.Nested(RefreshTokenResponseDataSchema, required=True, description="Datos del nuevo token")


class ErrorResponseSchema(Schema):
    """Esquema para respuestas de error"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=False)
    message = fields.String(required=True, description="Mensaje de error", example="Error en la autenticación")
    details = fields.String(required=False, description="Detalles adicionales del error")


class LogoutResponseSchema(Schema):
    """Esquema para respuesta al cerrar sesión"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=True)
    message = fields.String(required=True, description="Mensaje de respuesta", example="Sesión cerrada exitosamente")


class ErrorResponseSchema(Schema):
    """Esquema para respuestas de error"""
    success = fields.Boolean(required=True, description="Éxito de la operación", example=False)
    message = fields.String(required=True, description="Mensaje de error", example="Error en la autenticación")
    details = fields.String(required=False, description="Detalles adicionales del error")