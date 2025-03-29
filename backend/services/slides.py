import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def generate_notes_from_slides(slides):
    generated_notes = []
    for slide in slides:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=slide
        )
        generated_notes.append(response)
    return generated_notes
