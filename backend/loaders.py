import os
import fitz
import pytesseract
import cv2
from PIL import Image

from docx import Document
from pptx import Presentation

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langdetect import detect

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def detect_lang(text):
    try:
        return detect(text)
    except:
        return "unknown"


def extract_pdf(path):

    doc = fitz.open(path)

    text = ""

    for page in doc:

        text += page.get_text()

        images = page.get_images(full=True)

        for img in images:

            xref = img[0]

            base = doc.extract_image(xref)

            img_bytes = base["image"]

            img_name = f"temp_{xref}.png"

            with open(img_name, "wb") as f:
                f.write(img_bytes)

            img = cv2.imread(img_name)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ocr = pytesseract.image_to_string(gray)

            text += "\n" + ocr

            os.remove(img_name)

    return text


def extract_docx(path):

    doc = Document(path)

    text = ""

    for p in doc.paragraphs:
        text += p.text + "\n"

    return text


def extract_ppt(path):

    prs = Presentation(path)

    text = ""

    for slide in prs.slides:

        for shape in slide.shapes:

            if hasattr(shape, "text"):
                text += shape.text + "\n"

    return text


def load_documents(folder):

    docs = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        if file.endswith(".txt"):
            text = open(path, encoding="utf-8").read()

        elif file.endswith(".pdf"):
            text = extract_pdf(path)

        elif file.endswith(".docx"):
            text = extract_docx(path)

        elif file.endswith(".pptx"):
            text = extract_ppt(path)

        else:
            continue

        lang = detect_lang(text)

        chunks = splitter.split_text(text)

        for c in chunks:

            docs.append(
                LCDocument(
                    page_content=c,
                    metadata={
                        "source": file,
                        "language": lang
                    }
                )
            )

    return docs