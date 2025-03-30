import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def detect_and_write_slides_from_video(file_path):
    prompt = ("Detect slides within this video."
              "For each change in slide, mark its timestamp in MM:SS format before writing notes."
              "Generate well-formatted and clean notes with titles/headers based off of the slides you detect."
              "If you detect no slides, do not generate any text.")

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, file_path],
        config={
            'response_mime_type': 'application/xml',
        }
    )
    return response.text
