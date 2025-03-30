import os
from google import genai
from dotenv import load_dotenv
import pytesseract
from pdf2image import convert_from_path

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)

prompt = ("Generate well-formatted and clean notes with titles and headers from the text that you are supplied with."
          "There may be mistakes in formatting and spelling as of right. Please correct them, if necessary.")


def parse_generate_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    generated_notes = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, text],
    )
    return generated_notes
# make sure this returns formatted text, be it JSON or other format NOT a string,
# unless there are no other options, or it actually formats it well
