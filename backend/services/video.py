import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def detect_and_write_slides_from_video(file_path):
    my_file = client.files.upload(file=file_path)
    prompt = ("Detect slides within this video."
              "For each change in slide, mark its timestamp in MM:SS format before writing notes."
              "Generate well-formatted and clean notes with titles/headers based off of the slides you detect."
              "If you detect no slides within the video, do not generate a response or generate an empty response.")

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, my_file]
    )
    return response.text
