import traceback

from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import abort
from werkzeug.exceptions import BadRequest

from .routes import financial_agent_bp
from .services import FinancialAgentService
from .schemas import (
    ChatMessageSchema, 
    ChatResponseSchema, 
    ChatErrorResponseSchema,
    GoalSchema,
    GoalListQueryParamsSchema,
    GoalListResponseSchema,
    GoalListErrorResponseSchema,
    ConversationHistorySchema,
    ConversationHistoryResponseSchema,
    ConversationHistoryErrorResponseSchema
)


@financial_agent_bp.route("/chat")
class ChatController(MethodView):
    @financial_agent_bp.arguments(ChatMessageSchema)
    @financial_agent_bp.response(200, ChatResponseSchema)
    @financial_agent_bp.response(500, ChatErrorResponseSchema)
    @jwt_required()
    def post(self, request_body):
        """Process a chat message with the financial agent"""
        try:
            user_id = get_jwt_identity()
            data, status_code = FinancialAgentService.process_message(request_body, user_id)# En el controlador, antes de jsonify
            if 'goal' in data and '_id' in data['goal']:
                del data['goal']['_id']
            return jsonify(data), status_code
        except ValueError as e:
            print(traceback.format_exc(), flush=True)
            raise BadRequest(description=f"Error: {str(e)}")
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="An unexpected error occurred.", details=str(e))


@financial_agent_bp.route("/goals")
class FinancialGoalsController(MethodView):
    @financial_agent_bp.arguments(GoalListQueryParamsSchema, location="query")
    @financial_agent_bp.response(200, GoalListResponseSchema)
    @financial_agent_bp.response(404, GoalListErrorResponseSchema)
    @financial_agent_bp.response(500, GoalListErrorResponseSchema)
    @jwt_required()
    def get(self, args):
        """Retrieve all financial goals for the current user"""
        try:
            user_id = get_jwt_identity()
            page = args.get('page', 1)
            per_page = args.get('rows', 10)
            data, status_code = FinancialAgentService.get_financial_goals(user_id, page, per_page)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="An unexpected error occurred.", details=str(e))


@financial_agent_bp.route("/goals/<string:goal_id>")
class FinancialGoalDetailController(MethodView):
    @financial_agent_bp.response(200, GoalSchema)
    @financial_agent_bp.response(404, GoalListErrorResponseSchema)
    @financial_agent_bp.response(500, GoalListErrorResponseSchema)
    @jwt_required()
    def get(self, goal_id):
        """Retrieve a specific financial goal by ID"""
        try:
            user_id = get_jwt_identity()
            data, status_code = FinancialAgentService.get_financial_goal(goal_id, user_id)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="An unexpected error occurred.", details=str(e))


@financial_agent_bp.route("/conversation/<string:session_id>")
class ConversationHistoryController(MethodView):
    @financial_agent_bp.response(200, ConversationHistoryResponseSchema)
    @financial_agent_bp.response(404, ConversationHistoryErrorResponseSchema)
    @financial_agent_bp.response(500, ConversationHistoryErrorResponseSchema)
    @jwt_required()
    def get(self, session_id):
        """Retrieve conversation history for a specific session"""
        try:
            user_id = get_jwt_identity()
            data, status_code = FinancialAgentService.get_conversation_history(session_id, user_id)
            return jsonify(data), status_code
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            return abort(500, message="An unexpected error occurred.", details=str(e))