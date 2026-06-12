import os
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_images(pdf_path, output_dir):
    """
    Converts a PDF file to a list of images.
    Returns a list of paths to the saved images.
    """
    image_paths = []
    doc = fitz.open(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render page to an image (zoom factor can be adjusted for higher resolution)
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        
        output_path = os.path.join(output_dir, f"{base_name}_page_{page_num+1}.png")
        pix.save(output_path)
        image_paths.append(output_path)
        
    doc.close()
    return image_paths
