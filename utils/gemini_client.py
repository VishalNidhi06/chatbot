import google.generativeai as genai
import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini AI integration for online responses"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.available = False
        self.model = None
        
        # Validate API key
        if not self.api_key or self.api_key == '':
            logger.warning("Gemini API key not configured. AI features will be disabled.")
            return
        
        try:
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Test the API by listing available models (optional)
            self.model = genai.GenerativeModel(self.model_name)
            
            # Test if the model works with a simple prompt
            test_response = self.model.generate_content("Test")
            if test_response and test_response.text:
                self.available = True
                logger.info("Gemini AI initialized successfully")
            else:
                logger.warning("Gemini AI test failed")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.available = False
    
    def get_response(self, message, language='en'):
        """Get response from Gemini AI"""
        if not self.available:
            logger.warning("Gemini AI not available")
            return None
        
        try:
            # Add language instruction to the prompt
            language_instruction = self._get_language_instruction(language)
            full_prompt = f"{language_instruction}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Check if response is valid
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                logger.error("Empty response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None
    
    def _get_language_instruction(self, language):
        """Get language instruction for the prompt"""
        instructions = {
            'en': "Please respond in English.",
            'es': "Por favor, responde en español.",
            'fr': "Veuillez répondre en français.",
            'de': "Bitte antworte auf Deutsch.",
            'zh': "请用中文回复。",
            'ja': "日本語で返答してください。",
            'hi': "कृपया हिंदी में जवाब दें।"
        }
        return instructions.get(language, f"Please respond in {language} language.")
    
    def is_available(self):
        """Check if Gemini client is available"""
        return self.available