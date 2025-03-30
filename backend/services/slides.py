import os
import unicodedata
from google import genai
from dotenv import load_dotenv
import fitz  # pymupdf
from markdown2 import markdown
from fpdf import FPDF, HTMLMixin

# Load Gemini API key
load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

# Markdown-friendly PDF output
class MarkdownPDF(FPDF, HTMLMixin):
    pass

def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

# 🔥 Updated Gemini prompt
prompt = (
    "You will be given raw slide text from a lecture PDF. "
    "Generate **clean, professional Markdown-formatted notes** that can be converted into a PDF.\n\n"
    "Please:\n"
    "- Organize content into clear sections with `#`, `##`, or `###` headers\n"
    "- Use `**bold**` or `*italics*` for emphasis\n"
    "- Use bullet points (`-`) and numbered lists (`1.`) where appropriate\n"
    "- Include timestamps in MM:SS format if mentioned\n"
    "- Clean up grammar, spelling, and formatting issues\n"
    "- Make it visually readable and scannable\n\n"
    "Format all output in valid Markdown. This Markdown will be converted directly into a PDF document."
)

def parse_generate_pdf(pdf_path):
    print("📄 Parsing PDF text...")
    doc = fitz.open(pdf_path)
    text = ""
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        text += page.get_text() + "\n"

    print("🤖 Generating Markdown notes from Gemini...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, text]
    )
    markdown_notes = response.text

    # Save as PDF
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    notes_pdf = "lecture_notes.pdf"
    html = markdown(markdown_notes)
    html = clean_text(html)

    print("📄 Saving notes as PDF...")
    pdf = MarkdownPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.write_html(html)
    pdf.output(notes_pdf)

    return markdown_notes