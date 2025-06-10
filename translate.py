# translation_script.py
import json
from typing import Dict, Any, List
import os
from mistralai import Mistral
from dotenv import load_dotenv
from tqdm import tqdm
import spacy

# Load environment variables from .env file
load_dotenv(override=True)

# Load SpaCy model for Italian
nlp = spacy.load("it_core_news_sm")

def extract_sentences(text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def load_json_content(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

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

def translate_sentences(sentences: List[str], api_key: str) -> List[str]:
    translations = []
    for sentence in tqdm(sentences, desc="Translating sentences"):
        translation = translate_text(sentence, api_key)
        translations.append(translation)
    return translations

def process_and_translate(json_file_path: str, translated_json_file_path: str, api_key: str) -> None:
    # Load the JSON content
    json_content = load_json_content(json_file_path)

    # Concatenate all markdown content from all pages
    full_text = " ".join([page["markdown"] for page in json_content["pages"]])

    # Extract sentences
    sentences = extract_sentences(full_text)

    # Translate each sentence
    translated_sentences = translate_sentences(sentences, api_key)

    # Prepare the output structure
    output_data = {
        "sentences": [
            {"original": original, "translated": translated}
            for original, translated in zip(sentences, translated_sentences)
        ]
    }

    # Save the translated sentences
    with open(translated_json_file_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

# Define directories
original_dir = "original/json"
translated_dir = "translated/json"

# Ensure the translated directory exists
os.makedirs(translated_dir, exist_ok=True)

# Load JSON content from a file in the original directory
json_file_path = os.path.join(original_dir, 'ocr_response.json')

# Set your Mistral API key
api_key = os.getenv("MISTRAL_API_KEY")
if api_key is None:
    print("MISTRAL_API_KEY not found in the local .env file.")
    exit(1)

# Define the path for the translated JSON file
translated_json_file_path = os.path.join(translated_dir, 'translated_sentences.json')

# Process and translate
process_and_translate(json_file_path, translated_json_file_path, api_key)

print(f"Translated sentences saved to {translated_json_file_path}")
