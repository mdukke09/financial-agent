import traceback
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_smorest import abort

from .routes import auth_bp
from .services import AuthService
from .schemas import (
    LoginSchema, LoginResponseSchema, 
    RegisterSchema, RegisterResponseSchema,
    RefreshTokenSchema, RefreshTokenResponseSchema,
    LogoutResponseSchema,
    ErrorResponseSchema
)


@auth_bp.route("/login")
class LoginController(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.response(401, ErrorResponseSchema)
    @auth_bp.response(404, ErrorResponseSchema)
    @auth_bp.response(500, ErrorResponseSchema)
    def post(self, request_data):
        """Iniciar sesión y obtener tokens JWT"""
        try:
            email = request_data.get('email')
            password = request_data.get('password')
            
            data, status_code = AuthService.login(email, password)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="Error inesperado en el inicio de sesión", details=str(e))


@auth_bp.route("/register")
class RegisterController(MethodView):
    @auth_bp.arguments(RegisterSchema)
    @auth_bp.response(201, RegisterResponseSchema)
    @auth_bp.response(400, ErrorResponseSchema)
    @auth_bp.response(500, ErrorResponseSchema)
    def post(self, request_data):
        """Registrar un nuevo usuario"""
        try:
            data, status_code = AuthService.register(request_data)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="Error inesperado en el registro", details=str(e))


@auth_bp.route("/refresh-token")
class RefreshTokenController(MethodView):
    @auth_bp.arguments(RefreshTokenSchema)
    @auth_bp.response(200, RefreshTokenResponseSchema)
    @auth_bp.response(401, ErrorResponseSchema)
    @auth_bp.response(500, ErrorResponseSchema)
    @jwt_required(refresh=True)
    def post(self, request_data):
        """Refrescar token de acceso usando token de refresco"""
        try:
            refresh_token = request_data.get('refresh_token')
            data, status_code = AuthService.refresh_token(refresh_token)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="Error inesperado al refrescar el token", details=str(e))


@auth_bp.route("/me")
class UserProfileController(MethodView):
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.response(404, ErrorResponseSchema)
    @auth_bp.response(500, ErrorResponseSchema)
    @jwt_required()
    def get(self):
        """Obtener información del usuario actual"""
        try:
            user_id = get_jwt_identity()
            user = AuthService.get_user_by_id(user_id)
            
            if not user:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
            
            return jsonify({
                "success": True,
                "data": {
                    "user": {
                        "id": str(user.get('_id')),
                        "name": user.get('name', ''),
                        "email": user.get('email', ''),
                        "role": user.get('role', 'user')
                    }
                }
            }), 200
            
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="Error inesperado al obtener el perfil", details=str(e))


@auth_bp.route("/logout")
class LogoutController(MethodView):
    @auth_bp.response(200, LogoutResponseSchema)
    @auth_bp.response(500, ErrorResponseSchema)
    @jwt_required()
    def post(self):
        """Cerrar sesión (invalidar token)"""
        try:
            jti = get_jwt()["jti"]
            data, status_code = AuthService.logout(jti)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="Error inesperado al cerrar sesión", details=str(e))