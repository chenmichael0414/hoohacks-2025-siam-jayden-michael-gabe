import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

client.model = "gemini-2.0-flash"


def transcribe_audio(file_path):
    prompt = "Generate a transcript of only the speech in the video. Format it well. If the audio has no words, simply state that."
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, file_path]
    )
    return response.text
