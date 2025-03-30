import os
from google import genai
from dotenv import load_dotenv
from pptx import Presentation
from PIL import Image
import io

load_dotenv()
api_key = os.getenv('google_API_key')
client = genai.Client(api_key=api_key)


def detect_and_write_slides_from_pptx(file_path):
    prs = Presentation(file_path)
    slide_images = []
    for slide in prs.slides:
        for i, shape in slide.shapes:
            if hasattr(shape, "image"):
                img_data = slide.shapes[0].image.blob
                img = Image.open(io.BytesIO(img_data))
    prompt = (
        "Generate well-formatted and clean notes with titles and headers from the images that you are supplied with."
        "There may be mistakes in formatting and spelling as of right. Please correct them, if necessary."
        "Provide extensive timestamps in MM:SS format for each section of notes that you generate.")

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, slide_images],
    )
    return response.text
