import os
import argparse
from colorama import Fore, Style, init
from tqdm import tqdm
from modules.extract import extract_text_from_pdf
from modules.translate import process_and_translate
from modules.merge import create_pdf

# Initialize colorama
init(autoreset=True)

def validate_language_code(language_code):
    """Validate that the language code is an uppercase ISO language code."""
    if not isinstance(language_code, str):
        raise argparse.ArgumentTypeError("Language code must be a string.")
    if len(language_code) != 2:
        raise argparse.ArgumentTypeError("Language code must be 2 characters long.")
    if not language_code.isalpha():
        raise argparse.ArgumentTypeError("Language code must contain only alphabetic characters.")
    if not language_code.isupper():
        raise argparse.ArgumentTypeError("Language code must be in uppercase.")
    return language_code

def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== {text} ==={Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='Process and translate a PDF file.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing the input PDF file.')
    parser.add_argument('--source_language', type=validate_language_code, required=True, help='The source language of your document (uppercase ISO language code).')
    parser.add_argument('--target_language', type=validate_language_code, required=True, help='Language to translate the contents to (uppercase ISO language code).')
    parser.add_argument('--pdf_file', type=str, required=True, help='Name of the input PDF file.')
    parser.add_argument('--step', type=str, choices=['extract', 'translate', 'merge'], help='Specific step to execute')

    args = parser.parse_args()

    # Define paths
    pdf_path = os.path.join(args.input_dir, args.pdf_file)
    ocr_output_dir = "original/json"
    translated_dir = "translated/json"
    translated_json_file_path = os.path.join(translated_dir, 'translated_sentences.json')

    print_header("Starting PDF Processing")
    print_info(f"Input PDF: {args.pdf_file}")
    print_info(f"Source Language: {args.source_language}, Target Language: {args.target_language}")

    # Create output directories if they don't exist
    os.makedirs(ocr_output_dir, exist_ok=True)
    os.makedirs(translated_dir, exist_ok=True)
    print_success(f"Created directories: {ocr_output_dir}, {translated_dir}")

    if args.step is None or args.step == 'extract':
        print_header("Extracting Text from PDF")
        print_info(f"Input PDF Path: {pdf_path}")
        print_info(f"Output OCR Directory: {ocr_output_dir}")

        # Simulate progress bar for extraction
        with tqdm(total=100, desc="Extracting") as pbar:
            extract_text_from_pdf(pdf_path, ocr_output_dir)
            pbar.update(100)

        print_success("Text extraction completed successfully.")

    if args.step is None or args.step == 'translate':
        print_header("Translating Text")
        json_file_path = os.path.join(ocr_output_dir, 'ocr_response.json')
        print_info(f"Input JSON Path: {json_file_path}")
        print_info(f"Output Translated JSON Path: {translated_json_file_path}")

        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key is None:
            print_error("MISTRAL_API_KEY not found in the local .env file.")
            return

        source_language = args.source_language
        target_language = args.target_language
        print_info(f"Source Language: {source_language}, Target Language: {target_language}")

        # Simulate progress bar for translation
        with tqdm(total=100, desc="Translating") as pbar:
            process_and_translate(json_file_path, translated_json_file_path, api_key, source_language, target_language)
            pbar.update(100)

        print_success("Text translation completed successfully.")

    if args.step is None or args.step == 'merge':
        print_header("Creating PDF")
        base_name = os.path.splitext(args.pdf_file)[0]
        output_pdf_name = f"{base_name} - Translated.pdf"
        output_pdf_path = os.path.join("translated/pdf", output_pdf_name)

        print_info(f"Input Translated JSON Path: {translated_json_file_path}")
        print_info(f"Output PDF Path: {output_pdf_path}")

        # Simulate progress bar for PDF creation
        with tqdm(total=100, desc="Creating PDF") as pbar:
            create_pdf(translated_json_file_path, output_pdf_path)
            pbar.update(100)

        print_success("PDF creation completed successfully.")
        print_success(f"Process completed. Translated PDF saved at: {output_pdf_path}")

if __name__ == "__main__":
    main()
