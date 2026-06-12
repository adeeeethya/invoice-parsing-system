import easyocr

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

def extract_text(image):
    """
    Takes an image (either file path or numpy array) and extracts text using EasyOCR.
    Returns a single string with all extracted text concatenated.
    """
    results = reader.readtext(image)
    
    extracted_lines = []
    for (bbox, text, prob) in results:
        extracted_lines.append(text)
        
    raw_text = "\n".join(extracted_lines)
    return raw_text, extracted_lines
