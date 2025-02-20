import PyPDF2
import docx2txt
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pathlib
import os
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
POPPLER_PATH = '/usr/bin'

def extract_text_from_file(file_path):

    """
    Extracts text from a file based on its extension.
    Supports plain text, PDF, DOC/DOCX, and image formats.
    """
    ext = pathlib.Path(file_path).suffix.lower()

    if ext in [".txt", ".md", ".csv", ".json"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".pdf":
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            images = convert_from_path(file_path, poppler_path=POPPLER_PATH)  # Specify Poppler path
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        return text


    elif ext in [".doc", ".docx"]:
        file_content =docx2txt.process(file_path)
        return file_content

    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    else:
        return ''

    
