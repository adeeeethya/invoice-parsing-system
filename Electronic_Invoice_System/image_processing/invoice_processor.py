import cv2
import numpy as np
import math

def deskew_image(image):
    """
    Automatically deskews a rotated image.
    Uses Canny edge detection and probabilistic Hough transform.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)
    
    if lines is None:
        return image
        
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        # Keep angles near horizontal
        if -45 < angle < 45:
            angles.append(angle)
            
    if not angles:
        return image
        
    median_angle = np.median(angles)
    
    # If the angle is very small, no need to rotate
    if abs(median_angle) < 0.5:
        return image
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def process_invoice(image_path):
    """
    Advanced preprocessing for production-quality OCR.
    1. Read Image
    2. Deskew
    3. Resize (2x)
    4. Grayscale
    5. Blur
    6. Adaptive Thresholding
    7. Morphological operations (Noise removal)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # 1. Deskew
    deskewed = deskew_image(img)
    
    # 2. Resize 2x (upscale for better OCR resolution on small text)
    h, w = deskewed.shape[:2]
    resized = cv2.resize(deskewed, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    
    # 3. Grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # 4. Light blur to remove high frequency noise without destroying text edges
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # EasyOCR handles its own internal binarization using deep learning.
    # Applying hard adaptiveThreshold or morphological opening often destroys
    # the crisp text features that the OCR relies on, resulting in "wrong letters".
    
    return blurred
