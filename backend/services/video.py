import os
import ffmpeg
import cv2
import pytesseract
from fpdf import FPDF, HTMLMixin
from markdown2 import markdown
from google import genai 
from dotenv import load_dotenv
from .transcription import transcribe_audio_no_pdf
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

# 🔍 Perform OCR on frame
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
        "Using the transcript and visual slide content, generate clean, well-structured MARKDOWN notes. "
        "These notes will be automatically converted into a PDF document, so please use clear formatting that will look good when printed.\n\n"
        "Use the following Markdown formatting:\n"
        "- `#`, `##`, `###` for headers\n"
        "- `**bold**` and `*italics*` for emphasis\n"
        "- Bullet lists with `-` and numbered lists with `1.`\n"
        "- Code blocks where appropriate using triple backticks and language labels (e.g., ```c)\n\n"
        "Ensure the structure is logical and visually clean, as the final result will be presented as a professional PDF.\n\n"
        f"Transcript:\n{transcript}\n\nSlides:\n{slide_block}"
    )
    return prompt

# ✍️ Generate notes using Gemini
def generate_notes_from_prompt(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    return response.text

# 🧼 Clean problematic unicode characters
def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

# 📄 Save markdown content as a formatted PDF
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

# 🔄 Master pipeline to process a video into notes
def process_video(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = f"{base_name}_audio.mp3"
    notes_pdf = "lecture_notes.pdf"

    print("🎥 Extracting audio...")
    extract_audio(video_path, audio_path)

    print("📝 Transcribing audio...")
    transcript = transcribe_audio_no_pdf(audio_path)

    print("🖼️ Processing video frames and slide captions...")
    slides_info = detect_and_describe_slides(video_path)

    print("🤖 Generating prompt and notes...")
    prompt = build_notes_prompt(transcript, slides_info)
    notes_markdown = generate_notes_from_prompt(prompt)

    print("📄 Saving notes to PDF...")
    save_notes_as_pdf(notes_markdown, filename=notes_pdf)
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print("🗑️ MP3 file deleted successfully.")
    else:
        print("⚠️ File does not exist.")

    return notes_markdown
