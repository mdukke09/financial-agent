from flask_smorest import Blueprint

financial_agent_bp = Blueprint(
    "Financial Agent",
    __name__,
    url_prefix="/api/financial-agent",
    description="Financial Agent operations for managing financial goals through AI conversation"
)