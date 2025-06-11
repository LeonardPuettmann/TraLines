import re
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def create_pdf(input_json_path, output_pdf_path):
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 12

    light_gray = colors.Color(0.7, 0.7, 0.7)

    translated_style = ParagraphStyle(
        name='Translated',
        parent=styles['Normal'],
        textColor=light_gray,
        fontSize=9,
        leading=12,
        spaceBefore=6,
        spaceAfter=6
    )

    whole_style = ParagraphStyle(
        name='WholeContent',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceBefore=6,
        spaceAfter=6
    )

    for sentence_pair in data["sentences"]:
        original = sentence_pair["original"]
        translated = sentence_pair.get("translated", "")
        content_type = sentence_pair.get("content_type", "split")

        # Strip HTML tags from the original text
        original_clean = strip_html_tags(original)

        # Split original text by newlines and add each line as a separate paragraph
        original_lines = original_clean.split('\n')
        for line in original_lines:
            if line.strip():  # Only add non-empty lines
                original_paragraph = Paragraph(line, styles["Normal"])
                story.append(original_paragraph)

        if content_type == "split":
            # Strip HTML tags from the translated text
            translated_clean = strip_html_tags(translated)

            # Split translated text by newlines and add each line as a separate paragraph
            translated_lines = translated_clean.split('\n')
            for line in translated_lines:
                if line.strip():  # Only add non-empty lines
                    translated_paragraph = Paragraph(line, translated_style)
                    story.append(translated_paragraph)

        story.append(Spacer(1, 0.2*inch))

    doc.build(story)
    print(f"PDF generated successfully as {output_pdf_path}")

if __name__ == "__main__":
    input_json_path = 'translated/json/translated_sentences.json'
    output_pdf_path = 'output.pdf'
    create_pdf(input_json_path, output_pdf_path)
