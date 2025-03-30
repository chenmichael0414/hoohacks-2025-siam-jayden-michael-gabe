import os
import ffmpeg
import cv2
import pytesseract
from fpdf import FPDF
from google import genai
from dotenv import load_dotenv
from .transcription import transcribe_audio
import unicodedata

# Load Gemini API key from .env
load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

# 🔊 Extract MP3 audio from video file
def extract_audio(video_path, audio_path):
    ffmpeg.input(video_path).output(audio_path, format="mp3", acodec="libmp3lame").run(quiet=True)

# 🎞️ Extract frames from video every N seconds
def extract_frames(video_path, every_n_seconds=15, output_folder="frames"):
    os.makedirs(output_folder, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * every_n_seconds)

    frame_data = []
    count = 0
    success, frame = vidcap.read()
    while success:
        if count % interval == 0:
            timestamp = int(vidcap.get(cv2.CAP_PROP_POS_MSEC) // 1000)
            mmss = f"{timestamp // 60:02d}:{timestamp % 60:02d}"
            img_path = os.path.join(output_folder, f"frame_{mmss}.jpg")
            cv2.imwrite(img_path, frame)
            frame_data.append((mmss, img_path))
        success, frame = vidcap.read()
        count += 1
    return frame_data

# 🔍 Perform OCR and image captioning on frame
def analyze_frame(img_path):
    ocr_text = pytesseract.image_to_string(img_path)
    return ocr_text.strip()

# 🧾 Build slide content info from video
def detect_and_describe_slides(video_path):
    slides_info = []
    for timestamp, frame in extract_frames(video_path):
        ocr_text = analyze_frame(frame)
        slides_info.append((timestamp, ocr_text))
    return slides_info

# 🧠 Construct prompt from transcript and slide data
def build_notes_prompt(transcript, slides_info):
    slide_block = "\n".join(
        f"[{time}] OCR: {ocr}"
        for time, ocr in slides_info
    )
    prompt = (
        "Using the transcript and the visual content from the lecture slides below, "
        "generate clean, well-structured notes with section headers, bullet points, and clear explanations.\n\n"
        "Transcript:\n" + transcript + "\n\nSlides:\n" + slide_block
    )
    return prompt

# ✍️ Generate notes using Gemini
def generate_notes_from_prompt(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    return response.text

def clean_text(text):
    # Strip unsupported characters (like curly quotes, emojis, etc.)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")



def save_notes_as_pdf(notes_text, filename="lecture_notes.pdf"):
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
# 🔄 Master pipeline to process a video into notes
def process_video(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = f"{base_name}_audio.mp3"
    notes_pdf = f"{base_name}_notes.pdf"

    print("🎥 Extracting audio...")
    extract_audio(video_path, audio_path)

    print("📝 Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    print("🖼️ Processing video frames and slide captions...")
    slides_info = detect_and_describe_slides(video_path)

    print("🤖 Generating prompt and notes...")
    prompt = build_notes_prompt(transcript, slides_info)
    notes = generate_notes_from_prompt(prompt)

    print("📄 Saving notes to PDF...")
    save_notes_as_pdf(notes, filename=notes_pdf)

    return notes

# Example call:
# notes = process_video("my_lecture.mp4")
# print(notes)
