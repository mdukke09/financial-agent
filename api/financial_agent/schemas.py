from marshmallow import Schema, fields
from datetime import datetime


class ChatMessageSchema(Schema):
    """Schema for chat message requests"""
    message = fields.String(required=True, description="User message")
    session_id = fields.String(required=True, description="Session identifier")


class GoalSchema(Schema):
    """Schema for financial goal data"""
    id = fields.String(required=True, description="Goal identifier")
    nombre = fields.String(required=True, description="Goal name")
    valor = fields.Float(required=True, description="Target amount")
    tiempo = fields.String(required=True, description="Timeframe to achieve the goal")
    fecha_creacion = fields.DateTime(required=True, description="Creation date")
    descripcion = fields.String(required=True, description="Detailed description")
    categoria = fields.String(required=False, allow_none=True, description="Goal category")
    estado = fields.String(required=True, description="Current status", default="pendiente")


class ChatResponseSchema(Schema):
    """Schema for successful chat responses"""
    success = fields.Boolean(required=True, description="Status of the request", example=True)
    message = fields.String(required=True, description="AI assistant response")
    goal_complete = fields.Boolean(required=True, description="Whether the goal information is complete")
    goal = fields.Nested(GoalSchema, required=False, allow_none=True, description="Financial goal data if complete")
    goal_id = fields.String(required=False, allow_none=True, description="ID of the created goal if complete")


class ChatErrorResponseSchema(Schema):
    """Schema for chat error responses"""
    success = fields.Boolean(required=True, description="Status of the request", example=False)
    message = fields.String(required=True, description="Error message")
    details = fields.String(required=False, allow_none=True, description="Detailed error information")


class GoalListQueryParamsSchema(Schema):
    """Schema for goal list query parameters"""
    page = fields.Integer(required=False, description="Page number", default=1)
    rows = fields.Integer(required=False, description="Items per page", default=10)
    category = fields.String(required=False, description="Filter by category")
    status = fields.String(required=False, description="Filter by status")
    search = fields.String(required=False, description="Search text in goal name or description")


class GoalListDataSchema(Schema):
    """Schema for paginated goal list data"""
    total = fields.Integer(required=True, description="Total number of goals")
    data = fields.List(fields.Nested(GoalSchema), required=True, description="List of goals")


class GoalListResponseSchema(Schema):
    """Schema for successful goal list response"""
    success = fields.Boolean(required=True, description="Status of the request", example=True)
    message = fields.Nested(GoalListDataSchema, required=True, description="Response data")


class GoalListErrorResponseSchema(Schema):
    """Schema for goal list error responses"""
    success = fields.Boolean(required=True, description="Status of the request", example=False)
    message = fields.String(required=True, description="Error message")


class MessageSchema(Schema):
    """Schema for individual conversation messages"""
    role = fields.String(required=True, description="Message role (user/assistant)")
    content = fields.String(required=True, description="Message content")
    timestamp = fields.DateTime(required=True, description="Message timestamp")


class ConversationHistorySchema(Schema):
    """Schema for conversation history"""
    session_id = fields.String(required=True, description="Session identifier")
    user_id = fields.Integer(required=True, description="User identifier")
    messages = fields.List(fields.Nested(MessageSchema), required=True, description="Message history")
    created_at = fields.DateTime(required=True, description="When conversation started")
    updated_at = fields.DateTime(required=True, description="When conversation was last updated")


class ConversationHistoryResponseSchema(Schema):
    """Schema for successful conversation history response"""
    success = fields.Boolean(required=True, description="Status of the request", example=True)
    message = fields.Nested(ConversationHistorySchema, required=True, description="Conversation data")


class ConversationHistoryErrorResponseSchema(Schema):
    """Schema for conversation history error responses"""
    success = fields.Boolean(required=True, description="Status of the request", example=False)
    message = fields.String(required=True, description="Error message")