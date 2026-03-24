import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

class Translator:
    """Handle multilingual translation for the chatbot"""
    
    def __init__(self):
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.default_language = Config.DEFAULT_LANGUAGE
        self.use_api = Config.USE_TRANSLATION_API
        
        # Simple phrase dictionary for offline translation
        self.offline_phrases = self._load_offline_phrases()
    
    def _load_offline_phrases(self):
        """Load offline translation phrases"""
        return {
            'en': {
                'hello': 'Hello!',
                'how are you': 'How are you?',
                'thank you': 'Thank you!',
                'goodbye': 'Goodbye!',
                'sorry': 'Sorry!',
                'help': 'How can I help you?'
            },
            'es': {
                'hello': '¡Hola!',
                'how are you': '¿Cómo estás?',
                'thank you': '¡Gracias!',
                'goodbye': '¡Adiós!',
                'sorry': '¡Lo siento!',
                'help': '¿Cómo puedo ayudarte?'
            },
            'fr': {
                'hello': 'Bonjour!',
                'how are you': 'Comment allez-vous?',
                'thank you': 'Merci!',
                'goodbye': 'Au revoir!',
                'sorry': 'Désolé!',
                'help': 'Comment puis-je vous aider?'
            },
            'de': {
                'hello': 'Hallo!',
                'how are you': 'Wie geht es dir?',
                'thank you': 'Danke!',
                'goodbye': 'Auf Wiedersehen!',
                'sorry': 'Entschuldigung!',
                'help': 'Wie kann ich helfen?'
            },
            'zh': {
                'hello': '你好！',
                'how are you': '你好吗？',
                'thank you': '谢谢！',
                'goodbye': '再见！',
                'sorry': '对不起！',
                'help': '我能帮你什么？'
            },
            'ja': {
                'hello': 'こんにちは！',
                'how are you': 'お元気ですか？',
                'thank you': 'ありがとう！',
                'goodbye': 'さようなら！',
                'sorry': 'ごめんなさい！',
                'help': 'どのようにお手伝いできますか？'
            },
            'hi': {
                'hello': 'नमस्ते!',
                'how are you': 'आप कैसे हैं?',
                'thank you': 'धन्यवाद!',
                'goodbye': 'अलविदा!',
                'sorry': 'माफ़ कीजिये!',
                'help': 'मैं आपकी कैसे मदद कर सकता हूँ?'
            }
        }
    
    def translate_text(self, text, target_language, source_language='auto'):
        """Translate text to target language"""
        if not text or target_language == source_language:
            return text
        
        # If translation API is disabled or text is short, use offline translation
        if not self.use_api or len(text) < 50:
            return self._offline_translate(text, target_language)
        
        try:
            # Try using translation API
            url = Config.TRANSLATION_API_URL
            
            payload = {
                'q': text,
                'source': source_language if source_language != 'auto' else 'auto',
                'target': target_language,
                'format': 'text'
            }
            
            response = requests.post(url, data=payload, timeout=Config.TRANSLATION_API_TIMEOUT)
            
            if response.status_code == 200:
                translated = response.json()
                return translated.get('translatedText', text)
            else:
                logger.warning(f"Translation API failed with status {response.status_code}")
                return self._offline_translate(text, target_language)
                
        except requests.RequestException as e:
            logger.error(f"Translation API error: {e}")
            return self._offline_translate(text, target_language)
        except Exception as e:
            logger.error(f"Unexpected translation error: {e}")
            return text
    
    def _offline_translate(self, text, target_language):
        """Simple offline translation for common phrases"""
        text_lower = text.lower().strip()
        
        # Check if it's a common phrase
        for phrase_key, translation in self.offline_phrases.get(target_language, {}).items():
            if phrase_key in text_lower:
                return translation
        
        # If no match found, return original text
        return text
    
    def detect_language(self, text):
        """Detect language of given text with improved fallback"""
        if not text:
            return self.default_language
        
        # Simple keyword-based detection for common languages
        language_keywords = {
            'es': ['hola', 'como', 'estás', 'gracias', 'adiós', 'por favor'],
            'fr': ['bonjour', 'comment', 'merci', 'au revoir', 's\'il vous plaît'],
            'de': ['hallo', 'wie', 'danke', 'auf wiedersehen', 'bitte'],
            'zh': ['你好', '谢谢', '再见', '帮助', '怎么样'],
            'ja': ['こんにちは', 'ありがとう', 'さようなら', '助けて'],
            'hi': ['नमस्ते', 'धन्यवाद', 'अलविदा', 'मदद']
        }
        
        text_lower = text.lower()
        
        # Check for keywords
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return lang
        
        # Try API detection if available
        if self.use_api:
            try:
                url = "https://libretranslate.com/detect"
                response = requests.post(url, data={'q': text}, timeout=3)
                
                if response.status_code == 200:
                    detections = response.json()
                    if detections and len(detections) > 0:
                        best_match = max(detections, key=lambda x: x.get('confidence', 0))
                        detected_lang = best_match.get('language', self.default_language)
                        
                        if detected_lang in self.supported_languages:
                            return detected_lang
            except Exception as e:
                logger.debug(f"Language detection API failed: {e}")
        
        return self.default_language
    
    def get_supported_languages(self):
        """Get list of supported languages for translation"""
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'hi': 'Hindi'
        }
        
        return [{
            'code': code,
            'name': language_names.get(code, code)
        } for code in self.supported_languages]
    
    def get_language_name(self, language_code):
        """Get full name of language from code"""
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'hi': 'Hindi'
        }
        return language_names.get(language_code, language_code)
    
    def prepare_multilingual_prompt(self, user_message, user_language):
        """Prepare a prompt that ensures AI responds in the correct language"""
        if user_language == 'en':
            return user_message
        
        # Add language instruction to the prompt
        language_instructions = {
            'es': 'Por favor, responde en español.',
            'fr': 'Veuillez répondre en français.',
            'de': 'Bitte antworte auf Deutsch.',
            'zh': '请用中文回复。',
            'ja': '日本語で返答してください。',
            'hi': 'कृपया हिंदी में जवाब दें।'
        }
        
        instruction = language_instructions.get(user_language, f'Please respond in {user_language} language.')
        return f"{instruction}\n\nUser: {user_message}"
    
    def translate_response(self, response, user_language, original_language='en'):
        """Translate chatbot response to user's language"""
        if not response or user_language == original_language:
            return response
        
        # Try to detect if translation is needed
        if self.detect_language(response) == user_language:
            return response
        
        return self.translate_text(response, user_language, original_language)