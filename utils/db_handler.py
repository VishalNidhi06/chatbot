import json
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Handle JSON database operations"""
    
    def __init__(self):
        self.db_path = Config.QA_DATABASE_PATH
        self.languages_path = Config.LANGUAGES_PATH
        self.data = self.load_database()
        self.languages = self.load_languages()
    
    def load_database(self):
        """Load QA database from JSON file with better error handling"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded database with {len(data)} languages")
                    return data
            else:
                logger.warning(f"Database file not found: {self.db_path}")
                return self._create_default_database()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in database file: {e}")
            return self._create_default_database()
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return self._create_default_database()
    
    def _create_default_database(self):
        """Create default database structure"""
        default_data = {
            "en": [
                {"question": "hello", "answer": "Hello! How can I help you today?"},
                {"question": "how are you", "answer": "I'm doing great! Thanks for asking."},
                {"question": "bye", "answer": "Goodbye! Have a great day!"}
            ]
        }
        
        # Try to save default database
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            logger.info("Created default database file")
        except Exception as e:
            logger.error(f"Failed to create default database: {e}")
        
        return default_data
    
    def load_languages(self):
        """Load language configurations with fallback"""
        try:
            if os.path.exists(self.languages_path):
                with open(self.languages_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Languages file not found: {self.languages_path}")
                return self._create_default_languages()
        except Exception as e:
            logger.error(f"Error loading languages: {e}")
            return {'en': {'name': 'English'}}
    
    def _create_default_languages(self):
        """Create default language configuration"""
        default_langs = {
            "en": {"name": "English", "greeting": "Hello!", "online_mode": "AI Mode", "offline_mode": "Offline Mode"}
        }
        
        try:
            with open(self.languages_path, 'w', encoding='utf-8') as f:
                json.dump(default_langs, f, indent=2, ensure_ascii=False)
            logger.info("Created default languages file")
        except Exception as e:
            logger.error(f"Failed to create default languages: {e}")
        
        return default_langs
    
    def find_answer(self, message, language='en'):
        """Find answer in database with better matching"""
        try:
            message_lower = message.lower().strip()
            
            # Get language-specific Q&A
            qa_list = self.data.get(language, [])
            
            # Try exact match first
            for qa in qa_list:
                if qa['question'].lower() == message_lower:
                    return qa['answer']
            
            # Try partial match
            for qa in qa_list:
                if qa['question'].lower() in message_lower or message_lower in qa['question'].lower():
                    return qa['answer']
            
            # Try English database as fallback
            if language != 'en':
                en_qa_list = self.data.get('en', [])
                for qa in en_qa_list:
                    if qa['question'].lower() in message_lower or message_lower in qa['question'].lower():
                        return qa['answer']
            
            return None
        except Exception as e:
            logger.error(f"Error finding answer: {e}")
            return None
    
    def get_language_text(self, language, key):
        """Get language-specific text with fallback to English"""
        try:
            # Try to get from requested language
            if language in self.languages and key in self.languages[language]:
                return self.languages[language][key]
            
            # Fallback to English
            if 'en' in self.languages and key in self.languages['en']:
                return self.languages['en'][key]
            
            return ""
        except Exception:
            return ""
    
    def get_greeting(self, language):
        """Get greeting message for language"""
        return self.get_language_text(language, 'greeting')
    
    def get_mode_message(self, language, is_online):
        """Get mode-specific message"""
        if is_online:
            return self.get_language_text(language, 'online_mode')
        else:
            return self.get_language_text(language, 'offline_mode')
    
    def get_error_message(self, language):
        """Get error message"""
        return self.get_language_text(language, 'error') or "Sorry, something went wrong. Please try again."
    
    def get_no_match_message(self, language):
        """Get no match message"""
        return self.get_language_text(language, 'no_match') or "I don't have an answer for that. Please try rephrasing your question."