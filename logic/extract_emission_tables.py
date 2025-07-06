from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import json

def extract_from_pdf(pdf_path: str, page_ids=None):
    print(f"Loading PDF from: {pdf_path}")
    
    # This returns a list of page images (numpy arrays)
    pages = DocumentFile.from_pdf(pdf_path)
    print("Type of pages:", type(pages))  # <class 'list'>
    
    # If specific pages are requested, filter them
    if page_ids:
        selected_pages = [pages[i] for i in page_ids]
    else:
        selected_pages = pages

    # Load the OCR model
    model = ocr_predictor(pretrained=True)

    # Perform OCR on the selected pages
    result = model(selected_pages)
    full_json = result.export()

    return full_json

def save_json_result(result, output_path="data/glec_raw_output.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved raw OCR result to: {output_path}")
