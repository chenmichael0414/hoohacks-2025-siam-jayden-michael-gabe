import os

from fpdf import FPDF
from pydub import AudioSegment
from google import genai
from dotenv import load_dotenv
import tempfile
import os
import unicodedata
from fpdf import FPDF, HTMLMixin
from markdown2 import markdown
from pydub import AudioSegment
from dotenv import load_dotenv
from google import genai
import tempfile

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

CHUNK_DURATION_MS = 25 * 60 * 1000  # 25 minutes in milliseconds

import os

def build_notes_prompt(transcript, slides_info):
    slide_block = "\n".join(f"[{time}] OCR: {ocr}" for time, ocr in slides_info)
    prompt = (
        "Using the transcript and visual slide content, generate clean, well-structured MARKDOWN notes. "
        "These notes will be converted into a PDF, so use formatting that looks great when printed.\n\n"
        "Use Markdown:\n"
        "- `#`, `##`, `###` for headers\n"
        "- `**bold**` and `*italics*` for emphasis\n"
        "- Lists with `-` or `1.`\n"
        "- Use code blocks where appropriate (` ```c `)\n"
        "Try to use color-friendly formatting for printed output if possible.\n\n"
        f"Transcript:\n{transcript}\n\nSlides:\n{slide_block}"
    )
    return prompt


def generate_notes_from_prompt(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    return response.text


def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


class MarkdownPDF(FPDF, HTMLMixin):
    pass


def save_notes_as_pdf(notes_markdown, filename="lecture_notes.pdf"):
    html = markdown(notes_markdown)
    html = clean_text(html)

    pdf = MarkdownPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.write_html(html)
    pdf.output(filename)

def generate_notes(audio_path):
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    notes_pdf = f"{base_name}_notes.pdf"
    associated_video = f"{base_name}.mp4"

    print("🧠 Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    print("✍️ Building prompt and generating markdown notes...")
    prompt = build_notes_prompt(transcript, [])
    markdown_notes = generate_notes_from_prompt(prompt)

    print("📄 Saving notes as PDF...")
    save_notes_as_pdf(markdown_notes, filename=notes_pdf)

    return notes_pdf


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
    prompt = build_notes_prompt(full_transcript, [])
    markdown_notes = generate_notes_from_prompt(prompt)

    print("📄 Saving notes as PDF...")
    save_notes_as_pdf(markdown_notes)


    return full_transcript
