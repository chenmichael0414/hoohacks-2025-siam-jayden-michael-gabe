# 🧠 Lecture2Learn

A web app that converts lecture videos, PDFs, PowerPoints, or audio files into organized, professional Markdown notes and downloadable PDFs — powered by OCR, audio transcription, and Gemini AI.

## 🚀 Features

- 🎥 Upload **video (.mp4, .mov)** and extract:
  - Transcripts from speech (using Gemini)
  - Slide text from frames (via OCR)
- 🎙️ Upload **audio (.mp3)** and generate full transcripts + notes
- 📄 Upload **PDF** or **PPTX** lecture slides
  - Gemini reformats them into clean Markdown notes
- 📄 Output is automatically saved as a **PDF** and shown in-browser
- 🔁 Fully automated backend using Flask + threaded processing
- ✨ Beautifully styled with Bulma CSS + dynamic routing

---

## 🧪 Tech Stack

- **Frontend**: HTML, Jinja2, Bulma CSS
- **Backend**: Python, Flask
- **AI**: Google Gemini API
- **OCR**: Tesseract
- **PDF Generation**: Markdown → HTML → PDF with `fpdf` + `markdown2`
- **Deployment Ready**: Works on Render.com with `/tmp/` file handling

---

## How to run
- create a virtual environment in python
- type in python(3) backend/app.py

