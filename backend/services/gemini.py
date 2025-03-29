import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in 150 words"
)
print(response.text)
