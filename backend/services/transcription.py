import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def transcribe_audio(file_path):
    prompt = "Generate a transcript of only the speech in the video. Format it well using clean verbatim."
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, file_path],
        config={
            'response_mime_type': 'application/xml',
        }
    )
    return response.text
