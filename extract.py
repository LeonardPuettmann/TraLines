# extraction_script.py
import base64
import json
import os
from mistralai import Mistral
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image
import io
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv(override=True)

def encode_image(image):
    """Encode the image to base64."""
    try:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_json_response(page_number, page_content, output_path):
    """Save or append the page content to a JSON file."""
    try:
        # Load existing data if the file exists
        if os.path.exists(output_path):
            with open(output_path, 'r') as json_file:
                data = json.load(json_file)
        else:
            data = {"pages": [], "progress": {"current_page": 0}}

        # Append new page content with the page number
        data["pages"].append({"page_number": page_number+1, "markdown": page_content})

        # Update progress
        data["progress"]["current_page"] = len(data["pages"])

        # Save the updated data
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"Error saving JSON response: {e}")

# Path to your PDF
pdf_path = r"original/pdf/Umberto Eco - Il Nome Della Rosa.pdf"
output_dir = "original/json"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

api_key = os.getenv("MISTRAL_API_KEY")
if api_key is None:
    print("MISTRAL_API_KEY not found in the local .env file.")
    exit(1)

client = Mistral(api_key=api_key)

try:
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Define the output JSON file path
    output_path = os.path.join(output_dir, "ocr_response.json")

    # Load the current progress
    start_page = 0
    if os.path.exists(output_path):
        with open(output_path, 'r') as json_file:
            data = json.load(json_file)
            start_page = data["progress"]["current_page"]

    # Process each page with tqdm progress bar
    for page_number in tqdm(range(start_page, len(pdf_document)), initial=start_page, total=len(pdf_document)):
        page = pdf_document.load_page(page_number)  # Load the current page
        pix = page.get_pixmap()  # Render the page as a pixmap

        # Convert the pixmap to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Encode the image to base64
        base64_image = encode_image(img)
        if base64_image is None:
            continue

        # Process the image with the OCR API
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/png;base64,{base64_image}"
            },
            include_image_base64=True
        )

        # Extract and save the markdown content of the page
        for page in ocr_response.pages:
            save_json_response(page_number, page.markdown, output_path)

except Exception as e:
    print(f"Error processing OCR: {e}")

finally:
    pdf_document.close()
