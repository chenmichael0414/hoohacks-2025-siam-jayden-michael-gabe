import os
from pydub import AudioSegment
from google import genai
from dotenv import load_dotenv
import tempfile

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

CHUNK_DURATION_MS = 25 * 60 * 1000  # 25 minutes in milliseconds


def split_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), CHUNK_DURATION_MS):
        chunk = audio[i:i + CHUNK_DURATION_MS]
        chunks.append(chunk)
    return chunks


def transcribe_chunk(chunk, index):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        chunk.export(temp_file.name, format="mp3")
        my_file = client.files.upload(file=temp_file.name)

        prompt = (
            "Generate a transcript of only the speech in the audio file. "
            "Format it well using clean verbatim. "
            "If there is no speech in the audio file, do not generate a response or generate an empty response."
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, my_file]
        )

        os.remove(temp_file.name)
        return f"\n--- Segment {index + 1} ---\n" + response.text


def transcribe_audio(file_path):
    print("🔪 Splitting audio into 25-minute chunks...")
    chunks = split_audio(file_path)
    full_transcript = ""

    for i, chunk in enumerate(chunks):
        print(f"🧠 Transcribing chunk {i + 1}/{len(chunks)}...")
        full_transcript += transcribe_chunk(chunk, i)

    return full_transcript
