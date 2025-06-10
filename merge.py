import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, BalancedColumns, PageBreak
from reportlab.lib.units import inch

# Load the JSON file
with open('translated/json/translated_content.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a PDF document
doc = SimpleDocTemplate("output.pdf", pagesize=letter)
story = []

# Get the sample style sheet and modify the font size and other properties
styles = getSampleStyleSheet()
styles['Normal'].fontSize = 8  # Set the font size to 8
styles['Normal'].leading = 10  # Set the line spacing to 10

# Define the width for each column
column_width = (doc.width - 30) / 2  # Subtract padding and inner padding

# Iterate through the first 30 pages in the JSON file
for page in data["pages"][:20]:  # Only process the first 30 pages
    original = page["markdown"]
    translated = page["translated_markdown"]

    # Create Paragraph flowables for original and translated content with specified width
    original_paragraph = Paragraph(original, styles["Normal"])
    original_paragraph.wrapOn(doc, column_width, 1000)  # Wrap the paragraph to the column width
    original_paragraph.width = column_width  # Set the width of the paragraph

    translated_paragraph = Paragraph(translated, styles["Normal"])
    translated_paragraph.wrapOn(doc, column_width, 1000)  # Wrap the paragraph to the column width
    translated_paragraph.width = column_width  # Set the width of the paragraph

    # Create a BalancedColumns flowable with two columns for each pair
    balanced_columns = BalancedColumns(
        [original_paragraph, translated_paragraph],
        nCols=2,
        needed=72,
        spaceBefore=0,
        spaceAfter=0,
        showBoundary=0,
        leftPadding=10,
        rightPadding=10,
        topPadding=10,
        bottomPadding=10,
        innerPadding=10,
        name='BalancedColumns'
    )

    # Add the BalancedColumns flowable to the story
    story.append(balanced_columns)

    # Add a page break after each pair
    story.append(PageBreak())

# Build the PDF document
doc.build(story)
