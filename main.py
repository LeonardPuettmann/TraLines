import os
import argparse
from modules.extract import extract_text_from_pdf
from modules.translate import process_and_translate
from modules.merge import create_pdf

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process and translate a PDF file.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing the input PDF file.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory targeting the output PDF file.')
    parser.add_argument('--pdf_file', type=str, required=True, help='Name of the input PDF file.')
    parser.add_argument('--step', type=str, choices=['extract', 'translate', 'merge'], help='Specific step to execute')
    args = parser.parse_args()

    # Define paths
    pdf_path = os.path.join(args.input_dir, args.pdf_file)
    ocr_output_dir = "original/json"
    translated_dir = "translated/json"
    translated_json_file_path = os.path.join(translated_dir, 'translated_sentences.json')

    # Create output directories if they don't exist
    os.makedirs(ocr_output_dir, exist_ok=True)
    os.makedirs(translated_dir, exist_ok=True)

    if args.step is None or args.step == 'extract':
        # Extract text from PDF
        print("Extracting text from PDF...")
        extract_text_from_pdf(pdf_path, ocr_output_dir)

    if args.step is None or args.step == 'translate':
        # Translate text
        print("Translating text...")
        json_file_path = os.path.join(ocr_output_dir, 'ocr_response.json')
        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key is None:
            print("MISTRAL_API_KEY not found in the local .env file.")
            return
        process_and_translate(json_file_path, translated_json_file_path, api_key)

    if args.step is None or args.step == 'merge':
        # Define the output PDF path with the suffix " - Translated"
        base_name = os.path.splitext(args.pdf_file)[0]
        output_pdf_name = f"{base_name} - Translated.pdf"
        output_pdf_path = os.path.join(args.output_dir, output_pdf_name)

        # Create PDF
        print("Creating PDF...")
        create_pdf(translated_json_file_path, output_pdf_path)

if __name__ == "__main__":
    main()
