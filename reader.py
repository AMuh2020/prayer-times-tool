
# read text from an image using OCR (unfinished, not used in main project, Gemini would be better anyways)
import pytesseract
from PIL import Image

def read_image_text(image_path):
    # Open the image file
    img = Image.open(image_path)
    
    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(img)
    
    return text

if __name__ == "__main__":
    image_path = 'prayer_times_november.jpeg'  # Replace with your image path
    extracted_text = read_image_text(image_path)
    print("Extracted Text:")
    print(extracted_text)