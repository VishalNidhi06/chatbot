# test_gemini.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key preview: {api_key[:10]}..." if api_key else "None")

if not api_key or api_key == 'your_gemini_api_key_here':
    print("❌ ERROR: Please add your actual Gemini API key to the .env file")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n✅ API configured successfully")
    
    # Test with a simple prompt
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello, I am working!' in one sentence.")
    
    print(f"\n✅ Gemini response: {response.text}")
    print("\n🎉 Gemini is working correctly!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. API key doesn't have access to Gemini Pro")
    print("3. Network connectivity issues")