import json
from typing import Dict, Any
import os
from mistralai import Mistral
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(override=True)

# Load your JSON content
def load_json_content(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to translate text using Mistral API
def translate_text(text: str, api_key: str) -> str:
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Your task is to translate Italian into English. Keep the format of the text. Return nothing but an accurate translation. Only return the English translation!"
            },
            {
                "role": "user",
                "content": f"Translate this from Italian to English: {text}",
            },
        ]
    )

    return chat_response.choices[0].message.content

# Function to translate JSON content
def translate_json_content(content: Dict[str, Any], api_key: str, translated_json_file_path: str) -> None:
    for page in tqdm(content["pages"], desc="Translating pages"):
        markdown_content = page["markdown"]
        translated_content = translate_text(markdown_content, api_key)
        page["translated_markdown"] = translated_content

        # Save the updated content after each page translation
        with open(translated_json_file_path, 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)

    content["progress"]["current_page"] = len(content["pages"])

# Define directories
original_dir = "original/json"
translated_dir = "translated/json"

# Ensure the translated directory exists
os.makedirs(translated_dir, exist_ok=True)

# Load JSON content from a file in the original directory
json_file_path = os.path.join(original_dir, 'ocr_response.json')
json_content = load_json_content(json_file_path)

# Set your Mistral API key
api_key = os.getenv("MISTRAL_API_KEY")

# Define the path for the translated JSON file
translated_json_file_path = os.path.join(translated_dir, 'translated_content.json')

# Translate the JSON content
translate_json_content(json_content, api_key, translated_json_file_path)

print(f"Translated content saved to {translated_json_file_path}")
