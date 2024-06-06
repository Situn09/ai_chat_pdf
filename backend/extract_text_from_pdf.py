import fitz  # PyMuPDF
import sys

# Function to extract text from each page of the PDF
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    text = ""

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    return text

# Example usage
# pdf_path = "./uploaded_files/Blind 75 notes.pdf"
# extracted_text = extract_text_from_pdf(pdf_path)
# print(extracted_text)

sys.modules[__name__]=extract_text_from_pdf