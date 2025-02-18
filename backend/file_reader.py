import PyPDF2
import docx2txt
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pathlib

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:/poppler/poppler-24.08.0/Library/bin"  

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
        # docx2txt extracts text from DOCX; DOC may need conversion
        return docx2txt.process(file_path)

    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path)
        # Use pytesseract to perform OCR on the image
        return pytesseract.image_to_string(image)

    
