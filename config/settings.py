import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask
FLASK_HOST = os.getenv('APP_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('APP_PORT', 4000))
FLASK_DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'

# Deepseek API
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-r1/deepseek-r1-lite-chat')

# MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'financial_goals_db')
GOALS_COLLECTION = 'financial_goals'
CONVERSATIONS_COLLECTION = 'conversations'

# JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour by default
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days by default
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days by default
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']