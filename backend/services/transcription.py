import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def transcribe_audio(file_path):
    my_file = client.files.upload(file=file_path)
    prompt = ("Generate a transcript of only the speech in the audio file. Format it well using clean verbatim."
              "Provide extensive timestamps in MM:SS format for each line of speech that you transcribe."
              "If there is no speech in the audio file, do not generate a response or generate an empty response.")
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, my_file]
    )
    return response.text
