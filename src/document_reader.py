import PyPDF2
import re
import csv

# Function to extract Q&A from a PDF file
def extract_qa_from_pdf(file_path):
    questions_answers = []

    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        num_pages = reader.numPages

        for i in range(num_pages):
            page = reader.getPage(i)
            text = page.extractText()

            # Regex to identify questions and answers (example pattern)
            qa_pairs = re.findall(r'(Q\d+:\s+)(.*?)(?=\nQ\d+:|\n$)', text, re.DOTALL)

            for qa in qa_pairs:
                question = qa[0].strip()
                answer = qa[1].strip()
                questions_answers.append((question, answer))

    return questions_answers

# Example usage
file_path = 'path_to_your_pdf_file.pdf'
qa_data = extract_qa_from_pdf(file_path)

# Save to CSV
with open('questions_answers.csv', 'w', newline='', '') as file:
    writer = csv.writer(file)
    writer.writerow(['Question', 'Answer'])
    for qa in qa_data:
        writer.writerow(qa)
