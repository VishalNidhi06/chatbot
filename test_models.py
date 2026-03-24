# test_working_model.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ No API key found")
    exit(1)

print("=" * 60)
print("Testing Working Gemini Models")
print("=" * 60)

genai.configure(api_key=api_key)

# Models that worked in your list
models_to_test = [
    'models/gemini-2.5-flash',
    'models/gemini-2.5-pro',
    'models/gemini-2.0-flash',
    'models/gemini-flash-latest',
]

print("\nTesting models with a simple query...\n")

for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...")
        model = genai.GenerativeModel(model_name)
        
        # Test with a simple question
        response = model.generate_content("What is the capital of France? Answer in one word.")
        
        if response and response.text:
            print(f"✅ SUCCESS! {model_name} is working!")
            print(f"Response: {response.text}")
            print("-" * 60)
        else:
            print(f"⚠️ {model_name} returned empty response")
            
    except Exception as e:
        print(f"❌ {model_name} failed: {str(e)}")
        print("-" * 60)

print("\n" + "=" * 60)
print("Recommendation: Use 'gemini-2.5-flash' as it's fast and reliable")
print("=" * 60)