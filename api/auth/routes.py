from flask_smorest import Blueprint

auth_bp = Blueprint(
    "Auth",
    __name__,
    url_prefix="/api/auth",
    description="Operaciones de autenticación y gestión de tokens"
)