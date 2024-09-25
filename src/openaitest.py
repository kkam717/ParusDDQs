from openai import OpenAI
import pandas as pd
import tabula
from dotenv import load_dotenv
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# Load environment variables and set up OpenAI client
load_dotenv()

client = OpenAI()

client2 = OpenAI()


# Extract tables from PDF
pdf_path = 'DDQs/splitPDF.pdf'  # Replace with your PDF path
tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

# Combine all tables into a single string for GPT-4
all_tables_text = "\n".join([table.to_string(index=False) for table in tables])

system_message = "You are a virtual assistant skilled in interpreting and responding to due diligence questionnaires. For each question, you will give an answer and a confidence level as a percentage. Do you understand?"

# Initial query to GPT-4
initial_query = """
Using the information in this DDQ table, I want to use a language learning model to automate filling out other due diligence questions. All of the next inputs that I will give you are going to be DDQs relating to the above document. If a question has an alternative phrasing in the above document, and you have a high confidence level that it is asking the same thing, paste the answer from the equivalent question in the document. Otherwise, use your own judgement to give an answer to the question using all of the information in the document. For each answer, always give a confidence level as a percentage. Do you understand?
"""

# Function to get response from GPT-4
def get_gpt4_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4",  # GPT-4 model
        messages=[
            {"role": "system", "content": system_message + all_tables_text},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# Get initial response from GPT-4
print(get_gpt4_response(initial_query))

correction_sys_message = "You are a virtual assistant that corrects spelling and grammar. I will give you phrases, and you will correct them if needed, and if not, you will return back the same phrase. Otherwise, just return the corrected phrase on its own. Here is the phrase: \n "

# Function to correct questions ocr
def correct_questions(question):
    completion = client2.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": correction_sys_message},
            {"role": "user", "content": question}
        ]
    )

    return completion.choices[0].message.content

# Function to extract questions from a PDF table
def extract_questions_from_pdf(pdf_path):
    # Read tables from the PDF
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    if not tables:
        raise ValueError("No tables found in the provided PDF")

    # Assuming the first table in the PDF is the one with questions
    questions_table = tables[0]

    # Extracting questions from the first column
    questions = questions_table.iloc[:, 0].tolist()  # assuming questions are in the first column

    # for i in range(len(questions)):
        # questions[i] = correct_questions(questions[i])

    return questions

# Example path to the PDF with questions
questions_pdf_path = 'DDQs/splitPDF.pdf'  # Replace with your actual PDF path

print(1)

# Extract questions from the provided PDF
try:
    requests = extract_questions_from_pdf(questions_pdf_path)
except ValueError as e:
    print(f"Error: {e}")
    requests = []  # fallback to an empty list if there's an error
  

print(requests)

# Collect responses
responses = [get_gpt4_response(req) for req in requests]

# Prepare data for the table
styles = getSampleStyleSheet()
data = [["Request", "Response"]] + [[Paragraph(req, styles['Normal']), Paragraph(resp, styles['Normal'])] for req, resp in zip(requests, responses)]

# Create a PDF file with responses in tabular form
file_name = 'ddq_responses.pdf'
document = SimpleDocTemplate(file_name, pagesize=letter)

# Create table and style
table = Table(data, colWidths=[2.5*inch, 4.75*inch])
style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('VALIGN', (0, 0), (-1, -1), 'TOP')
])
table.setStyle(style)

# Add table to PDF
elements = [table]

# Build PDF
document.build(elements)

print(f"PDF created: {file_name}")