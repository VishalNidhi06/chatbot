from flask import Flask, render_template, request, jsonify
import logging
import sys
from config import Config
from utils.internet_checker import InternetChecker
from utils.gemini_client import GeminiClient
from utils.db_handler import DatabaseHandler
from utils.translator import Translator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
internet_checker = InternetChecker()
gemini_client = GeminiClient()
db_handler = DatabaseHandler()
translator = Translator()

@app.route('/')
def index():
    """Render chat interface"""
    return render_template('index.html')

@app.route('/api/check_internet', methods=['GET'])
def check_internet():
    """Check internet connectivity"""
    try:
        is_connected = internet_checker.check_and_log()
        return jsonify({
            'status': 'success',
            'online': is_connected,
            'message': 'Internet available' if is_connected else 'No internet connection'
        })
    except Exception as e:
        logger.error(f"Error checking internet: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'status': 'error', 'message': 'No message provided'}), 400
        
        logger.info(f"Received message in {language}: {message[:100]}")
        
        # Detect user's language
        detected_lang = translator.detect_language(message)
        logger.info(f"Detected language: {detected_lang}")
        
        # Check internet connectivity
        is_online = internet_checker.is_connected()
        
        if is_online and gemini_client.is_available():
            # Online mode - Use Gemini AI
            logger.info("Using Gemini AI for response")
            
            # Prepare multilingual prompt
            enhanced_prompt = translator.prepare_multilingual_prompt(message, language)
            ai_response = gemini_client.get_response(enhanced_prompt, language)
            
            if ai_response:
                # Ensure response is in user's language if needed
                final_response = translator.translate_response(ai_response, language, detected_lang)
                
                return jsonify({
                    'status': 'success',
                    'response': final_response,
                    'mode': 'online',
                    'source': 'gemini_ai',
                    'detected_language': detected_lang
                })
            else:
                # Fallback to database if AI fails
                logger.warning("Gemini failed, falling back to database")
                db_response = db_handler.find_answer(message, language)
                
                if db_response:
                    return jsonify({
                        'status': 'success',
                        'response': db_response,
                        'mode': 'offline_fallback',
                        'source': 'database',
                        'detected_language': detected_lang
                    })
                else:
                    return jsonify({
                        'status': 'success',
                        'response': db_handler.get_no_match_message(language),
                        'mode': 'offline_fallback',
                        'source': 'database',
                        'detected_language': detected_lang
                    })
        else:
            # Offline mode - Use local database
            logger.info("Using local database for response")
            db_response = db_handler.find_answer(message, language)
            
            if db_response:
                return jsonify({
                    'status': 'success',
                    'response': db_response,
                    'mode': 'offline',
                    'source': 'database',
                    'detected_language': detected_lang
                })
            else:
                no_match_msg = db_handler.get_no_match_message(language)
                return jsonify({
                    'status': 'success',
                    'response': no_match_msg,
                    'mode': 'offline',
                    'source': 'database',
                    'detected_language': detected_lang
                })
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    try:
        languages = translator.get_supported_languages()
        
        return jsonify({
            'status': 'success',
            'languages': languages,
            'default': Config.DEFAULT_LANGUAGE
        })
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/greeting', methods=['GET'])
def get_greeting():
    """Get greeting message"""
    try:
        language = request.args.get('language', 'en')
        is_online = internet_checker.is_connected() and gemini_client.is_available()
        
        greeting = db_handler.get_greeting(language)
        if not greeting:
            greeting = "Hello! How can I help you today?"
        
        mode_message = db_handler.get_mode_message(language, is_online)
        
        return jsonify({
            'status': 'success',
            'greeting': greeting,
            'mode_message': mode_message,
            'online': is_online
        })
    except Exception as e:
        logger.error(f"Error getting greeting: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Multilingual Chatbot Application")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)