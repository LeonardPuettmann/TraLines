import base64
import json
import os
from mistralai import Mistral
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image
import io
from tqdm import tqdm

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
        if os.path.exists(output_path):
            with open(output_path, 'r') as json_file:
                data = json.load(json_file)
        else:
            data = {"pages": [], "progress": {"current_page": 0}}

        data["pages"].append({"page_number": page_number+1, "markdown": page_content})
        data["progress"]["current_page"] = len(data["pages"])

        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"Error saving JSON response: {e}")

def extract_text_from_pdf(pdf_path, output_dir):
    """Extract text from PDF and save to JSON."""
    load_dotenv(override=True)
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key is None:
        print("MISTRAL_API_KEY not found in the local .env file.")
        return

    client = Mistral(api_key=api_key)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ocr_response.json")

    try:
        pdf_document = fitz.open(pdf_path)
        start_page = 0
        if os.path.exists(output_path):
            with open(output_path, 'r') as json_file:
                data = json.load(json_file)
                start_page = data["progress"]["current_page"]

        for page_number in tqdm(range(start_page, len(pdf_document)), initial=start_page, total=len(pdf_document)):
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            base64_image = encode_image(img)
            if base64_image is None:
                continue

            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64_image}"
                },
                include_image_base64=True
            )

            for page in ocr_response.pages:
                save_json_response(page_number, page.markdown, output_path)

    except Exception as e:
        print(f"Error processing OCR: {e}")
    finally:
        pdf_document.close()

if __name__ == "__main__":
    pdf_path = r"original/pdf/Umberto Eco - Il Nome Della Rosa.pdf"
    output_dir = "original/json"
    extract_text_from_pdf(pdf_path, output_dir)
