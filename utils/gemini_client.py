import google.generativeai as genai
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini AI integration for online responses"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.available = False
        self.model = None
        self.error_message = None
        self.quota_exhausted = False
        self.retry_after = 0
        
        # Log API key status
        if not self.api_key:
            self.error_message = "No API key configured"
            logger.error("Gemini API key not configured")
            return
        
        if self.api_key == 'YOUR_API_KEY_HERE' or self.api_key == '':
            self.error_message = "Default/empty API key"
            logger.error("Default API key detected")
            return
        
        logger.info(f"API key loaded (length: {len(self.api_key)})")
        
        try:
            # Configure the API
            genai.configure(api_key=self.api_key)
            logger.info("Gemini API configured")
            
            # Prioritize models that are known to work
            working_models = [
                'models/gemini-flash-latest',
                'models/gemini-2.5-flash',
                'models/gemini-2.5-pro',
                'models/gemini-2.0-flash-001',
                'models/gemini-2.0-flash-lite-001',
                'models/gemini-flash-lite-latest',
                'models/gemini-pro-latest'
            ]
            
            # Try the configured model first
            models_to_try = []
            configured_model = f"models/{self.model_name}" if not self.model_name.startswith('models/') else self.model_name
            if configured_model not in working_models:
                models_to_try.append(configured_model)
            models_to_try.extend(working_models)
            
            # Remove duplicates
            seen = set()
            models_to_try = [x for x in models_to_try if not (x in seen or seen.add(x))]
            
            logger.info(f"Will try models in order: {models_to_try}")
            
            # Try each model until one works
            for model_path in models_to_try:
                try:
                    logger.info(f"Attempting to initialize model: {model_path}")
                    self.model = genai.GenerativeModel(model_path)
                    
                    # Test the model
                    logger.info(f"Testing {model_path}...")
                    test_response = self.model.generate_content("Say 'OK'")
                    
                    if test_response and hasattr(test_response, 'text') and test_response.text:
                        logger.info(f"✅ Successfully initialized with {model_path}")
                        self.model_name = model_path.replace('models/', '')
                        self.available = True
                        self.error_message = None
                        self.quota_exhausted = False
                        break
                    else:
                        logger.warning(f"{model_path} returned empty response")
                        
                except Exception as e:
                    error_msg = str(e)
                    if '429' in error_msg or 'quota' in error_msg.lower():
                        logger.warning(f"⚠️ Quota exceeded for {model_path}")
                        if 'retry_delay' in error_msg:
                            import re
                            match = re.search(r'retry_delay \{\s*seconds:\s*(\d+)', error_msg)
                            if match:
                                self.retry_after = int(match.group(1))
                        continue
                    else:
                        logger.warning(f"❌ Failed with {model_path}: {error_msg[:100]}")
                        continue
            
            if not self.available:
                if self.retry_after > 0:
                    self.error_message = f"Quota exceeded. Please try again in {self.retry_after} seconds"
                else:
                    self.error_message = "No working model found"
                logger.error(f"Could not initialize Gemini: {self.error_message}")
                
        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.available = False
    
    def get_response(self, message, language='en'):
        """Get response from Gemini AI"""
        if not self.available:
            if self.quota_exhausted:
                logger.warning(f"Gemini quota exhausted. Retry after: {self.retry_after}s")
            else:
                logger.warning(f"Gemini AI not available. Error: {self.error_message}")
            return None
        
        try:
            # Add language instruction to the prompt
            language_instruction = self._get_language_instruction(language)
            full_prompt = f"{language_instruction}\n\nUser: {message}\n\nAssistant:"
            
            logger.info(f"Sending request to Gemini (model: {self.model_name}, language: {language})")
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            # Check if response is valid
            if response and hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
                logger.info(f"✅ Gemini response received (length: {len(response_text)})")
                return response_text
            else:
                logger.error("Empty response from Gemini API")
                return None
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            
            if '429' in error_msg or 'quota' in error_msg.lower():
                self.quota_exhausted = True
            
            return None
    
    def _get_language_instruction(self, language):
        """Get language instruction for the prompt with Tamil support"""
        instructions = {
            'en': "Please respond in English.",
            'es': "Por favor, responde en español.",
            'fr': "Veuillez répondre en français.",
            'de': "Bitte antworte auf Deutsch.",
            'zh': "请用中文回复。",
            'ja': "日本語で返答してください。",
            'hi': "कृपया हिंदी में जवाब दें।",
            'ta': "தயவுசெய்து தமிழில் பதிலளிக்கவும்."  # Added Tamil instruction
        }
        return instructions.get(language, f"Please respond in {language} language.")
    
    def is_available(self):
        """Check if Gemini client is available"""
        return self.available and not self.quota_exhausted
    
    def get_status(self):
        """Get detailed status information"""
        return {
            'available': self.available,
            'quota_exhausted': self.quota_exhausted,
            'retry_after': self.retry_after,
            'error': self.error_message,
            'api_key_configured': bool(self.api_key and self.api_key != 'YOUR_API_KEY_HERE'),
            'model': self.model_name
        }