# pdf_generation_script.py
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

# Load the JSON file with translated sentences
with open('translated/json/translated_sentences.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a PDF document
doc = SimpleDocTemplate("output.pdf", pagesize=letter)
story = []

# Get the sample style sheet and modify the font size and other properties
styles = getSampleStyleSheet()
styles['Normal'].fontSize = 10  # Set the font size for original text
styles['Normal'].leading = 12   # Set the line spacing

# Define a style for translated text (light grey)
translated_style = ParagraphStyle(
    name='Translated',
    parent=styles['Normal'],
    textColor=gray(0.7),  # Light grey
    fontSize=9,
    leading=12
)

# Iterate through each sentence pair
for sentence_pair in data["sentences"]:
    original = sentence_pair["original"]
    translated = sentence_pair["translated"]

    # Create Paragraph flowables for original and translated content
    original_paragraph = Paragraph(original, styles["Normal"])
    translated_paragraph = Paragraph(translated, translated_style)

    # Add the original and translated paragraphs to the story
    story.append(original_paragraph)
    story.append(translated_paragraph)

    # Add a blank space between sentence pairs
    story.append(Spacer(1, 0.2*inch))

# Build the PDF document
doc.build(story)

print("PDF generated successfully as output.pdf")
