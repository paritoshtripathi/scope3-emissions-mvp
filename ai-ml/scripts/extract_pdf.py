from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: Extracted text from the PDF or an empty string if an error occurs.
    """
    if not pdf_path:
        print("No PDF path provided.")
        return ""

    try:
        text = []
        reader = PdfReader(pdf_path)
        for page_number, page in enumerate(reader.pages, start=1):
            extracted_text = page.extract_text() or ""
            text.append(extracted_text)
            print(f"Extracted text from page {page_number}.")
        return " ".join(text)
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return ""
