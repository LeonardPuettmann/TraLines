Here is the raw markdown for the PDF Translation Tool documentation:

````markdown
# PDF Translation Tool

A tool to extract text from PDFs, translate it, and merge the translated text back into a new PDF.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [License](#license)
- [Contributing](#contributing)

## Installation

1. Clone the repository to your local machine.

```bash
git clone <repository-url>
```

2. Navigate to the project directory.

```bash
cd pdf-translation-tool
```

3. Install the required dependencies using pip.

```bash
pip install -r requirements.txt
```

4. Download the spaCy language model for Italian.

```bash
python -m spacy download it_core_news_sm
```

## Usage

To use the PDF Translation Tool, run the main script with the required arguments:

```bash
python main.py --input_dir path/to/pdf --pdf_file "filename.pdf"
```

### Command Line Arguments

- `--input_dir`: Directory containing the input PDF file (required).
- `--pdf_file`: Name of the input PDF file (required).

### Example

```bash
python main.py --input_dir original/pdf --pdf_file "Umberto Eco - Il Nome Della Rosa.pdf"
```

This command will:

1. Extract text from the PDF and save it to a JSON file.
2. Translate the text and save the translations to another JSON file.
3. Create a new PDF with the translated text, using the input file name with the suffix " - Translated.pdf".

## Project Structure

```plaintext
project/
│   .env
│   .gitignore
│   main.py
│   README.md
│   requirements.txt
├───modules
│   │   extract.py
│   │   merge.py
│   └───translate.py
├───original
│   ├───json
│   │       ocr_response.json
│   └───pdf
│           Umberto Eco - Il Nome Della Rosa.pdf
│
└───translated
    ├───json
    │       translated_sentences.json
    └───pdf
```

- `.env`: Environment variables file.
- `.gitignore`: Specifies intentionally untracked files to ignore.
- `main.py`: The main script that orchestrates the workflow.
- `README.md`: This readme file.
- `requirements.txt`: Lists all the dependencies required for the project.
- `modules/`: Directory containing the modules for extraction, translation, and merging.
  - `extract.py`: Script to extract text from PDFs.
  - `merge.py`: Script to merge the translated text back into a new PDF.
  - `translate.py`: Script to translate the extracted text.
- `original/`: Directory containing the input PDF files and extracted text in JSON format.
  - `json/`: Directory to store the extracted text in JSON format.
    - `ocr_response.json`: JSON file containing the extracted text.
  - `pdf/`: Directory containing the input PDF files.
    - `Umberto Eco - Il Nome Della Rosa.pdf`: Example input PDF file.
- `translated/`: Directory to store the translated text in JSON format and the final translated PDFs.
  - `json/`: Directory to store the translated text in JSON format.
    - `translated_sentences.json`: JSON file containing the translated text.
  - `pdf/`: Directory to store the final translated PDFs.

## Dependencies

The project requires the following Python packages:

- mistralai
- python-dotenv
- PyMuPDF (fitz)
- Pillow (PIL)
- tqdm
- spacy
- reportlab

You can install these dependencies using pip:

```bash
pip install mistralai python-dotenv PyMuPDF Pillow tqdm spacy reportlab
```

Additionally, you will need to download the spaCy language model for Italian:

```bash
python -m spacy download it_core_news_sm
```

## Environment Variables

The project uses environment variables to store sensitive information such as API keys. Create a `.env` file in the root directory of the project and add your Mistral API key:

```plaintext
MISTRAL_API_KEY=your_api_key_here
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
````