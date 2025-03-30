import os
from google import genai
from dotenv import load_dotenv
import fitz

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

prompt = ("Generate well-formatted and clean notes with titles and headers from the text that you are supplied with."
          "There may be mistakes in formatting and spelling as of right. Please correct them, if necessary."
          "Provide extensive timestamps in MM:SS format for each section of notes that you generate.")


def parse_generate_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)  # Load a page
        text += page.get_text() + "\n"  # Extract text from the page
    generated_notes = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, text],
    )
    return generated_notes.text
