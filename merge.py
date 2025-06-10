import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
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

# Define light gray color (70% gray)
light_gray = colors.Color(0.7, 0.7, 0.7)

# Define a style for translated text (light grey)
translated_style = ParagraphStyle(
    name='Translated',
    parent=styles['Normal'],
    textColor=light_gray,
    fontSize=9,
    leading=12,
    spaceBefore=6,  # Add some space before the paragraph
    spaceAfter=6    # Add some space after the paragraph
)

# For content that shouldn't be translated (whole content)
whole_style = ParagraphStyle(
    name='WholeContent',
    parent=styles['Normal'],
    fontSize=10,  # Same size as original text
    leading=12,
    spaceBefore=6,
    spaceAfter=6
)

# Iterate through each sentence pair
for sentence_pair in data["sentences"]:
    original = sentence_pair["original"]
    translated = sentence_pair.get("translated", "")
    content_type = sentence_pair.get("content_type", "split")

    # Create Paragraph flowables
    # Use <br/> tags to explicitly preserve line breaks (ReportLab will convert these to actual line breaks)
    original_text = original.replace('\n', '<br/>')
    original_paragraph = Paragraph(original_text, styles["Normal"])

    story.append(original_paragraph)

    # Only add the translation for split content
    if content_type == "split":
        # Replace newlines with <br/> for proper line breaks in PDF
        translated_text = translated.replace('\n', '<br/>')
        translated_paragraph = Paragraph(translated_text, translated_style)
        story.append(translated_paragraph)

    # Add a blank space between entries
    story.append(Spacer(1, 0.2*inch))

# Build the PDF document
doc.build(story)

print("PDF generated successfully as output.pdf")
