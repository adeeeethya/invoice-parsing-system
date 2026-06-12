import cv2
import numpy as np

def preprocess_image(image_path):
    """
    Reads an image and applies preprocessing steps (grayscale, blur, threshold)
    to improve OCR accuracy.
    Returns the preprocessed image.
    """
    # 1. Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
        
    # EasyOCR generally performs better without harsh adaptive thresholding
    # especially for digital PDFs converted to images.
    return img

def save_preprocessed_image(img, output_path):
    """
    Saves the preprocessed image to disk (optional, useful for debugging).
    """
    cv2.imwrite(output_path, img)
    return output_path
