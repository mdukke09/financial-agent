import json
import logging
from datetime import datetime
from bson.objectid import ObjectId
from openai import OpenAI

from models.financial_goals import FinancialGoal, Conversation
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL
from utils.prompt_templates import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class FinancialAgentService:
    @staticmethod
    def process_message(request_data, user_id):
        """
        Process a user message and generate an AI response
        
        Args:
            request_data (dict): Request data containing message and session_id
            user_id (str): User ID from JWT token
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            user_message = request_data.get('message')
            session_id = request_data.get('session_id')
            
            # Get conversation history
            conversation = FinancialAgentService._get_or_create_conversation(session_id, user_id)
            
            # Process message with Deepseek
            ai_response, is_goal_complete, financial_goal = FinancialAgentService._call_deepseek(
                user_message, 
                conversation.get('messages', [])
            )
            
            # Save messages to conversation history
            FinancialAgentService._save_conversation_messages(
                session_id, 
                user_id, 
                user_message, 
                ai_response
            )
            
            # Prepare response
            response_data = {
                "success": True,
                "message": ai_response,
                "goal_complete": is_goal_complete
            }
            
            # If goal is complete, save it to database
            if is_goal_complete and financial_goal:
                # Add session_id and user_id to goal data
                financial_goal['session_id'] = session_id
                financial_goal['user_id'] = user_id
                
                # Save to database
                goal_id = FinancialAgentService._save_financial_goal(financial_goal)
                response_data["goal_id"] = str(goal_id)
                response_data["goal"] = financial_goal
            
            return response_data, 200
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def get_financial_goals(user_id, page=1, per_page=10, filters=None):
        """
        Get all financial goals for a user with pagination
        
        Args:
            user_id (int): User ID 
            page (int): Page number
            per_page (int): Items per page
            filters (dict): Optional filters
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Build query
            query = {"user_id": user_id}
            
            # Apply filters if provided
            if filters:
                if 'category' in filters and filters['category']:
                    query['categoria'] = filters['category']
                if 'status' in filters and filters['status']:
                    query['estado'] = filters['status']
                if 'search' in filters and filters['search']:
                    search_text = filters['search']
                    query['$or'] = [
                        {"nombre": {"$regex": search_text, "$options": "i"}},
                        {"descripcion": {"$regex": search_text, "$options": "i"}}
                    ]
            
            # Get total count
            total = FinancialGoal.count_documents(query)
            
            # Get paginated data
            skip = (page - 1) * per_page
            goals = list(FinancialGoal.find(query).skip(skip).limit(per_page))
            
            # Convert ObjectId to string
            for goal in goals:
                goal['id'] = str(goal.pop('_id'))
            
            return {
                "success": True,
                "message": {
                    "total": total,
                    "data": goals
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error retrieving financial goals: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def get_financial_goal(goal_id, user_id):
        """
        Get a specific financial goal by ID
        
        Args:
            goal_id (str): Goal ID
            user_id (int): User ID for verification
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Find goal in database
            goal = FinancialGoal.find_one({"_id": ObjectId(goal_id), "user_id": user_id})
            
            if not goal:
                return {"success": False, "message": "Financial goal not found"}, 404
            
            # Convert ObjectId to string
            goal['id'] = str(goal.pop('_id'))
            
            return {"success": True, "message": goal}, 200
            
        except Exception as e:
            logger.error(f"Error retrieving financial goal: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    @staticmethod
    def get_conversation_history(session_id, user_id):
        """
        Get conversation history for a specific session
        
        Args:
            session_id (str): Session ID
            user_id (int): User ID for verification
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Find conversation in database
            conversation = Conversation.find_one({"session_id": session_id, "user_id": user_id})
            
            if not conversation:
                return {"success": False, "message": "Conversation not found"}, 404
            
            # Convert ObjectId to string
            conversation['id'] = str(conversation.pop('_id'))
            
            return {"success": True, "message": conversation}, 200
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return {"success": False, "message": str(e)}, 500
    
    # Método ajustado de _call_deepseek()

    @staticmethod
    def _call_deepseek(user_message, conversation_history):
        """
        Call Deepseek API to process user message using the OpenAI SDK
        
        Args:
            user_message (str): User message
            conversation_history (list): List of previous messages
            
        Returns:
            tuple: (ai_response, is_goal_complete, financial_goal)
        """
        try:
            # Initialize the OpenAI client with Deepseek configuration
            client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
            
            # Obtener fecha actual para el prompt
            current_date = datetime.now().strftime("%d/%m/%Y")
            system_prompt_with_date = SYSTEM_PROMPT.replace("{{CURRENT_DATE}}", current_date)
            
            # Format conversation history
            formatted_messages = [{"role": "system", "content": system_prompt_with_date}]
            
            # Add conversation history
            for message in conversation_history:
                if 'role' in message and 'content' in message:
                    formatted_messages.append({
                        "role": message['role'],
                        "content": message['content']
                    })
            
            # Add current user message
            formatted_messages.append({"role": "user", "content": user_message})
            
            # Log para depuración
            logger.info(f"Enviando solicitud a Deepseek con {len(formatted_messages)} mensajes")
            
            # Make the API call
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=1500,
                top_p=0.9
            )
        
            # Extract the response
            assistant_response = response.choices[0].message.content
            logger.info(f"Respuesta recibida de Deepseek. Buscando meta financiera...")
            
            # Check if response contains financial goal JSON
            is_goal_complete = False
            financial_goal = None
            
            # Usar expresión regular para extraer JSON después de META_FINANCIERA_JSON:
            import re
            
            # Patrones a buscar
            patterns = [
                # Patrón para META_FINANCIERA_JSON: seguido de ```json y luego el JSON
                r'META_FINANCIERA_JSON:\s*```json\s*(\{.*?\})\s*```',
                # Patrón para META_FINANCIERA_JSON: seguido directamente del JSON
                r'META_FINANCIERA_JSON:\s*(\{.*?\})',
                # Patrón para cuando hay otros caracteres entre la etiqueta y el JSON
                r'META_FINANCIERA_JSON:.*?(\{.*?\})',
                # Patrón para capturar JSON con comillas simples
                r'META_FINANCIERA_JSON:.*?(\{[^}]*\})'
            ]
            
            # Intentar cada patrón
            json_str = None
            for pattern in patterns:
                # Usar DOTALL para que . coincida también con saltos de línea
                match = re.search(pattern, assistant_response, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    logger.info(f"Patrón coincidente encontrado: {pattern}")
                    break
            
            if json_str:
                try:
                    # Limpiar posibles caracteres no JSON
                    json_str = json_str.strip()
                    
                    # Intentar limpiar malformaciones comunes
                    if not json_str.endswith('}'):
                        # Buscar la última llave de cierre
                        last_brace = json_str.rfind('}')
                        if last_brace > 0:
                            json_str = json_str[:last_brace+1]
                    
                    financial_goal = json.loads(json_str)
                    is_goal_complete = True
                    logger.info(f"Meta financiera extraída correctamente: {financial_goal}")
                    
                    # Limpiar el JSON de la respuesta para el usuario
                    # Usar el mismo patrón que coincidió para eliminarlo
                    for pattern in patterns:
                        assistant_response = re.sub(pattern, '', assistant_response, flags=re.DOTALL)
                        
                    # Limpiar líneas vacías extras que puedan haber quedado
                    assistant_response = re.sub(r'\n\s*\n', '\n\n', assistant_response)
                    assistant_response = assistant_response.strip()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing financial goal JSON: {e}")
                    logger.error(f"JSON intentado parsear: {json_str}")
            
            return assistant_response, is_goal_complete, financial_goal
            
        except Exception as e:
            logger.error(f"Error calling Deepseek API: {str(e)}")
            raise
    
    @staticmethod
    def _get_or_create_conversation(session_id, user_id):
        """
        Get or create a conversation for the given session_id and user_id
        
        Args:
            session_id (str): Session ID
            user_id (int): User ID
            
        Returns:
            dict: Conversation document
        """
        # Try to find existing conversation
        conversation = Conversation.find_one({"session_id": session_id, "user_id": user_id})
        
        # Create new conversation if not found
        if not conversation:
            now = datetime.now()
            conversation = {
                "session_id": session_id,
                "user_id": user_id,
                "messages": [],
                "created_at": now,
                "updated_at": now
            }
            Conversation.insert_one(conversation)
            
        return conversation
    
    @staticmethod
    def _save_conversation_messages(session_id, user_id, user_message, ai_response):
        """
        Save user message and AI response to conversation history
        
        Args:
            session_id (str): Session ID
            user_id (int): User ID
            user_message (str): User message
            ai_response (str): AI response
        """
        now = datetime.now()
        
        # Add user message
        Conversation.update_one(
            {"session_id": session_id, "user_id": user_id},
            {
                "$push": {
                    "messages": {
                        "role": "user",
                        "content": user_message,
                        "timestamp": now
                    }
                },
                "$set": {"updated_at": now}
            }
        )
        
        # Add assistant response
        Conversation.update_one(
            {"session_id": session_id, "user_id": user_id},
            {
                "$push": {
                    "messages": {
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": now
                    }
                },
                "$set": {"updated_at": now}
            }
        )
    
    @staticmethod
    def _save_financial_goal(goal_data):
        """
        Save financial goal to database
        
        Args:
            goal_data (dict): Financial goal data
            
        Returns:
            ObjectId: ID of inserted document
        """
        # Ensure required fields
        if 'fecha_creacion' not in goal_data:
            goal_data['fecha_creacion'] = datetime.now().isoformat()
        
        if 'estado' not in goal_data:
            goal_data['estado'] = 'pendiente'
        
        # Insert into database
        result = FinancialGoal.insert_one(goal_data)
        return str(result.inserted_id)