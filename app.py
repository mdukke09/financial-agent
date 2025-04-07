import logging
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config.settings import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, JWT_SECRET_KEY
# Después de registrar los blueprints
from api.financial_agent.controllers import financial_agent_bp
from api.auth.controllers import auth_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app outside function
app = Flask(__name__)

# Configure Flask app
app.config["API_TITLE"] = "Financial Agent API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Configure JWT
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ['access', 'refresh']

# Initialize extensions
api = Api(app)
jwt = JWTManager(app)
CORS(app)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200

api.register_blueprint(financial_agent_bp)
api.register_blueprint(auth_bp)

# Solo después de los imports añadir los manejadores de JWT
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    try:
        from models.blacklist import is_token_blacklisted
        jti = jwt_payload["jti"]
        return is_token_blacklisted(jti)
    except Exception as e:
        logger.error(f"Error en token_in_blocklist_loader: {str(e)}")
        return False
    
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "message": "El token ha expirado"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "success": False,
        "message": "Firma del token inválida"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "success": False,
        "message": "Token de acceso requerido"
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "message": "El token ha sido revocado"
    }), 401

# Log registered routes
logger.info("Rutas registradas:")
for rule in app.url_map.iter_rules():
    logger.info(f"{rule.endpoint}: {rule.methods} {rule.rule}")

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)