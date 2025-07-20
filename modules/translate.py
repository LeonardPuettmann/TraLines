import json
from typing import Dict, Any, List
import os
from mistralai import Mistral
from dotenv import load_dotenv
from tqdm import tqdm
import spacy
import time

load_dotenv(override=True)
nlp = spacy.load("it_core_news_sm")

LLM_MODEL = "mistral-small-latest"

CLASSIFICATION_SYSTEM_PROMPT = """
You are a text analysis assistant. Your task is to determine if the given text should be split into sentences for translation or treated as a whole.
Regular content includes paragraphs, sentences, and sections of text that form cohesive ideas and can be translated more accurately when split into individual sentences. Examples include main body text, chapters, sections, and paragraphs.
Other types of content include:
- Index: A list of terms and their locations in the document.
- Table of Contents: A list of chapters or sections with page numbers.
- Bibliography: A list of references or sources.
- Lists: Bulleted or numbered lists that should be kept together.
- Headers and Footers: Repeated text at the top or bottom of pages.
- Captions: Short descriptions accompanying images or tables.
Respond with 'split' if the text should be split into sentences for translation. Respond with 'whole' if the text should be treated as a whole.
"""

TRANSLATION_SYSTEM_PROMPT = """
Your task is to translate the given text from {source_language} into {target_language}. Follow these guidelines to ensure an accurate and consistent translation:
1. **Language Detection**: Identify and translate all text written in {source_language}. If there are segments in other languages, translate them into {target_language} as well.
2. **Format Preservation**: Maintain the original format of the text, including line breaks, paragraphs, bullet points, numbered lists, and any special formatting.
3. **Non-Translatable Elements**: Do not translate names of people, places, brands, and specific terms that should remain in their original language. However, ensure these are accurately represented in the {target_language} text.
4. **Accuracy and Fluency**: Provide an accurate translation that is fluent and natural in {target_language}. Ensure that the meaning of the original text is preserved.
5. **Special Characters and Symbols**: Keep all special characters, symbols, and punctuation marks as they appear in the original text.
6. **Ambiguities and Context**: If there are ambiguities in the text, use your best judgment to provide a translation that fits the context. If necessary, provide a note indicating any uncertainties.
Text to translate:
{text_to_translate}
Return nothing but an accurate translation. Only return the {target_language} translation!
"""

def extract_sentences(text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def load_json_content(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def llm_text_classification(text: str, api_key: str) -> bool:
    truncated_text = text if len(text) <= 2000 else text[:2000] + "... (truncated)"
    model = LLM_MODEL
    client = Mistral(api_key=api_key)
    prompt = f"""
    Analyze the following text and determine if it is regular content that should be split into sentences for translation, or if it is something else like an index, table of contents, bibliography, etc., that should be treated as a whole.
    Text:
    {truncated_text}

    Respond with one of these classes: 
    - 'split' if the text should be split into sentences.
    - 'whole' if it should be treated as a whole.
    """
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": CLASSIFICATION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    response = chat_response.choices[0].message.content.strip().lower()
    return response == "split"

def translate_text(text: str, api_key: str, source_language: str, target_language: str) -> str:
    model = LLM_MODEL
    client = Mistral(api_key=api_key)
    formatted_prompt = TRANSLATION_SYSTEM_PROMPT.format(
        source_language=source_language,
        target_language=target_language,
        text_to_translate=text
    )
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": formatted_prompt
            },
            {
                "role": "user",
                "content": f"Translate this from {source_language} to {target_language}: {text}",
            },
        ]
    )
    return chat_response.choices[0].message.content

def process_and_translate(json_file_path: str, translated_json_file_path: str, api_key: str, source_language: str, target_language: str) -> None:
    json_content = load_json_content(json_file_path)
    if os.path.exists(translated_json_file_path):
        with open(translated_json_file_path, 'r', encoding='utf-8') as file:
            output_data = json.load(file)
    else:
        output_data = {"sentences": [], "progress": {"last_processed_page": -1}}

    last_processed_page = output_data["progress"]["last_processed_page"]
    start_page = last_processed_page + 1
    pages = json_content["pages"]

    if start_page >= len(pages):
        print("All pages have already been processed.")
        return

    for page_index in tqdm(range(start_page, len(pages)), desc="Processing pages", initial=start_page, total=len(pages)):
        page = pages[page_index]
        page_text = page["markdown"]

        if not page_text.strip():
            output_data["progress"]["last_processed_page"] = page_index
            with open(translated_json_file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, ensure_ascii=False, indent=4)
            continue

        text_type = llm_text_classification(page_text, api_key)

        try:
            if text_type == "split":
                sentences = extract_sentences(page_text)
                for sentence in sentences:
                    translated_sentence = translate_text(sentence, api_key, source_language, target_language)
                    output_data["sentences"].append({
                        "original": sentence,
                        "translated": translated_sentence,
                        "content_type": "split"
                    })
            elif text_type == "whole":
                translated_text = translate_text(page_text, api_key, source_language, target_language)
                output_data["sentences"].append({
                    "original": page_text,
                    "translated": translated_text,
                    "content_type": "whole"
                })

            output_data["progress"]["last_processed_page"] = page_index
            with open(translated_json_file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error processing page {page_index + 1}: {str(e)}")
            output_data["progress"]["last_processed_page"] = page_index - 1
            with open(translated_json_file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, ensure_ascii=False, indent=4)
            raise

if __name__ == "__main__":
    original_dir = "original/json"
    translated_dir = "translated/json"
    os.makedirs(translated_dir, exist_ok=True)
    json_file_path = os.path.join(original_dir, 'ocr_response.json')
    translated_json_file_path = os.path.join(translated_dir, 'translated_sentences.json')
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key is None:
        print("MISTRAL_API_KEY not found in the local .env file.")
        exit(1)

    process_and_translate(json_file_path, translated_json_file_path, api_key, source_language, target_language)
    print(f"Translation process completed. Results saved to {translated_json_file_path}")
