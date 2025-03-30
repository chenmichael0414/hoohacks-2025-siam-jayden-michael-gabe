import os

from fpdf import FPDF
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


def transcript_as_pdf(notes_text, filename="lecture_notes.pdf"):
    class NotesPDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 16)
            self.cell(0, 10, "Lecture Notes", ln=True, align="C")
            self.ln(5)

        def chapter_title(self, title):
            self.set_font("Arial", 'B', 14)
            self.set_text_color(33, 37, 41)
            self.cell(0, 10, title, ln=True)
            self.ln(2)

        def bullet_point(self, text):
            self.set_font("Arial", '', 12)
            self.set_text_color(50, 50, 50)
            self.cell(5)  # indent
            self.multi_cell(0, 8, u"\u2022 " + text)
            self.ln(1)

        def paragraph(self, text):
            self.set_font("Arial", '', 12)
            self.set_text_color(0)
            self.multi_cell(0, 8, text)
            self.ln(3)

    def clean_text(text):
        import re
        return re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ASCII for FPDF compatibility

    pdf = NotesPDF()
    pdf.add_page()

    # Clean up problematic characters
    notes_text = clean_text(notes_text)

    # Split into sections (using double newlines as block breaks)
    blocks = notes_text.strip().split("\n\n")
    for block in blocks:
        if block.startswith("### "):  # custom header notation if used
            title = block.replace("### ", "").strip()
            pdf.chapter_title(title)
        elif block.startswith("- "):
            for line in block.split("\n"):
                if line.startswith("- "):
                    pdf.bullet_point(line[2:].strip())
        else:
            pdf.paragraph(block)

    pdf.output(filename)


def transcribe(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    transcript_pdf = f"{base_name}_transcript.pdf"
    full_transcript = transcribe_audio(file_path)
    transcript_as_pdf(full_transcript, transcript_pdf)

