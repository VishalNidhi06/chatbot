import os
from dotenv import load_dotenv
import os.path

# Load environment variables
load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
    
    # Application Configuration
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    QA_DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'qa_database.json')
    LANGUAGES_PATH = os.path.join(BASE_DIR, 'data', 'languages.json')
    LOG_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'chatbot.log')
    
    # Internet Check Configuration
    INTERNET_CHECK_URL = 'https://www.google.com'
    INTERNET_CHECK_TIMEOUT = 5
    
    # Supported Languages - ADD TAMIL HERE
    SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'hi', 'ta']  # Added 'ta' for Tamil
    DEFAULT_LANGUAGE = 'en'
    
    # Translation Configuration
    USE_TRANSLATION_API = True
    TRANSLATION_API_URL = 'https://libretranslate.com/translate'
    TRANSLATION_API_TIMEOUT = 5
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        log_dir = os.path.dirname(Config.LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        data_dir = os.path.dirname(Config.QA_DATABASE_PATH)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

# Call this when config is imported
Config.ensure_directories()