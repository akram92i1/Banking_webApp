import os
import glob
from langchain_core.documents import Document

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: OCR libraries (pytesseract, Pillow, pdf2image) not installed. Using text fallback only.")

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    if not HAS_OCR:
        return "OCR Libraries not available."
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')
        return text
    except Exception as e:
        print(f"Error executing OCR on {image_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using pdf2image and Tesseract OCR."""
    if not HAS_OCR:
        return "OCR Libraries not available."
    try:
        images = pdf2image.convert_from_path(pdf_path)
        full_text = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, config='--psm 6')
            full_text.append(text)
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error executing OCR on {pdf_path}: {e}")
        return ""

def load_flyers_with_ocr(directory: str) -> list[Document]:
    """
    Looks for PDF and Image flyers in the directory.
    If OCR libraries are present, performs OCR and returns Documents.
    Falls back to existing .txt files if no media is found or OCR is unavailable.
    """
    documents = []
    if not os.path.exists(directory):
        return documents

    # Handle PDFs
    for ext in ["*.pdf"]:
        for file in glob.glob(os.path.join(directory, ext)):
            text = extract_text_from_pdf(file)
            if text:
                basename = os.path.basename(file)
                store = basename.split("_")[0].lower() if "super_c" not in basename.lower() else "super_c"
                documents.append(Document(page_content=text, metadata={"source": file, "store": store, "type": "ocr_pdf"}))

    # Handle Images
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        for file in glob.glob(os.path.join(directory, ext)):
            text = extract_text_from_image(file)
            if text:
                basename = os.path.basename(file)
                store = basename.split("_")[0].lower() if "super_c" not in basename.lower() else "super_c"
                documents.append(Document(page_content=text, metadata={"source": file, "store": store, "type": "ocr_image"}))

    return documents
