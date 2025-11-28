# config.py
import os

# Secret key for session management
SECRET_KEY = 'your-secret-key-change-this-in-production-2024'

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/news_portal'

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size