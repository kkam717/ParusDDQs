import tabula  # PyMuPDF for PDF extraction
import pandas as pd
from dotenv import load_dotenv
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = FastAPI()

# Setup CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str


load_dotenv()
client = OpenAI()

global_data_context = ""
global_data_type = ""
global_file_loc = ""
sheets = None

# File to store persisted training data
DATA_FILE = "DDQs/saved_training_data.json"


categories = ['General Information', 'UCITS', 'Marketing (HR, Client base)', 'Legal', 'ESG', 'Trading', 'Operations', 'Compliance', 'IT', 'Investments']


try:
    sheets = pd.read_excel('DDQs/DDQ MastersheetEB.xlsx', sheet_name=None) 
except:
    sheets = ""


# Helper to save both context and data type
def save_data_context():
    data = {
        "context": global_data_context,
        "data_type": global_data_type  # Save the type of data as well
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)  # Use JSON format for structured storage


# Load saved data on startup (create the file if it doesn't exist or it's empty)
if not os.path.exists(DATA_FILE):
    # Create an empty JSON file if it doesn't exist
    with open(DATA_FILE, 'w') as f:
        json.dump({"context": "", "data_type": ""}, f)
else:
    # Check if the file is empty or contains invalid JSON
    try:
        with open(DATA_FILE, 'r') as f:
            saved_data = json.load(f)
            global_data_context = saved_data.get("context", "")
            global_data_type = saved_data.get("data_type", "")
    except json.JSONDecodeError:
        # Handle empty or invalid JSON by reinitializing the file with defaults
        with open(DATA_FILE, 'w') as f:
            json.dump({"context": "", "data_type": ""}, f)
        global_data_context = ""
        global_data_type = ""

def spreadsheet_data_to_context(category, sheets):
    """
    Converts spreadsheet data for a given category into a string context.
    This function needs to be tailored based on how the data is structured and what's relevant.
    """
    if category in sheets:
        selected_columns = sheets[category].iloc[:, :2].dropna()
        df = pd.DataFrame(selected_columns)
        df.reset_index(drop=True, inplace=True)
        if 'index' in df.columns:
            df.drop('index', axis=1, inplace=True)
        
        # Convert the dataframe to a string in a meaningful way
        # This could involve selecting certain columns, rows, or formatting
        context = df.to_string(index=False)  # Placeholder, customize this
        return str(context)
    return ""


def parse_ddq(pdf_path, output_path, output):
    tables = tabula.read_pdf(pdf_path, pages='all', lattice=True, multiple_tables=True)
    parsed = ""
    
    if output:
        with open(output_path, "w") as file:
            for df in tables:
                df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]

                head = [str(i) for i in range(len(df.columns))]

                df = df.T.reset_index().T.reset_index(drop=True)
                df.columns = head


                for i in range(len(df)):
                    for j in head:
                        file.write(str(df[j][i]) + "\n\n")
                        parsed += str(df[j][i]) + "\n"
                
                file.write("\n\n")
                parsed += "\n"
    else:
        for df in tables:
            df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]

            head = [str(i) for i in range(len(df.columns))]

            df = df.T.reset_index().T.reset_index(drop=True)
            df.columns = head


            for i in range(len(df)):
                for j in head:
                    parsed += str(df[j][i]) + "\n"
            
            file.write("\n\n")
            parsed += "\n"
    
    return parsed


def get_gpt4_response(prompt, all_tables_text):
    system_message = "You are a virtual assistant skilled in interpreting and responding to due diligence questionnaires. Here is the information you will need to answer the question: "
    completion = client.chat.completions.create(
        model="gpt-4-turbo-preview",  # GPT-4 model
        messages=[
            {"role": "system", "content": system_message + all_tables_text},
            {"role": "user", "content": "Here is the question for you to answer: \n" + prompt + "\nDo not guess the answer. Use the information previously given. Avoid using any formatting other than standard string formatting."}
        ]
    )
    return completion.choices[0].message.content

def get_questions(content):
    system_message = "You are going to receive a file of questions. Clean them up by returning them in the format Question: followed by the question content, and a new line after each one. Do not return any other text. "
    completion = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": content}
        ]
    )
    text = completion.choices[0].message.content

    questions_list = [question.strip() for question in text.split("Question:") if question.strip()]

    responses = []

    for question in questions_list:
        print('q')

        response = get_gpt4_response(question, global_data_context)
        responses.append(response)

    return [questions_list, responses]


def produce_pdf(requests, responses, file_name):
    styles = getSampleStyleSheet()
    # Adjust the style for better content fit
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontSize=10,  # Consider reducing the font size if content still overflows
        leading=12,  # Adjust leading accordingly
        wordWrap='CJK',  # Allows for better word wrapping
    )

    data = [["Request", "Response"]]
    for req, resp in zip(requests, responses):
        # Wrap the content with KeepInFrame to manage overflow
        req_content = KeepInFrame(0, 0, [Paragraph(req, custom_style)], mode='shrink')
        resp_content = KeepInFrame(0, 0, [Paragraph(resp, custom_style)], mode='shrink')

        data.append([req_content, resp_content])


    if os.path.exists(file_name):
        os.remove(file_name)
    
    document = SimpleDocTemplate(
        file_name,
        pagesize=letter,
        rightMargin=50,  # Adjusted margins to provide more space
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    table = Table(data, colWidths=[2.5*inch, 4.75*inch], repeatRows=1)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])
    table.setStyle(table_style)

    elements = [table]
    document.build(elements)

    print(f"PDF created: {file_name}")


@app.post("/api/response/")
async def get_response(query: Query):
    global global_data_context, global_data_type, global_file_loc, sheets
    try:
        question = query.query
        
        response = ""

        if global_data_type == "pdf":
            response = get_gpt4_response(question, global_data_context)

        else:
            response = get_gpt4_response(question, global_data_context)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF containing unanswered questions, send the questions to OpenAI for answers,
    and return a new PDF containing both the questions and the answers.
    """
    global global_data_context

    # Step 1: Save the uploaded PDF file
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    file_loc = os.path.join(uploads_dir, file.filename)
    
    try:
        with open(file_loc, "wb") as buffer:
            buffer.write(await file.read())
        
        # Step 2: Parse the uploaded PDF to extract questions
        parsed_questions = parse_ddq(file_loc, "uploads/parsedQuestions.txt", True)
        
        # Clean up the parsed questions to ensure they are in the correct format
        questions, _ = get_questions(parsed_questions)

        if not questions:
            return {"message": "No questions found in the uploaded PDF."}

        # Step 3: Send each question to OpenAI and collect answers
        answers = []
        for question in questions:
            response = get_gpt4_response(question, global_data_context)

            answers.append(response)

        # Step 4: Generate a new PDF with the questions and answers
        file_name = 'DDQs/ddq_responses.pdf'
        produce_pdf(questions, answers, file_name=file_name)
        
        # Step 5: Return the new PDF file
        return FileResponse(file_name, media_type='application/pdf', filename="answered_ddq_responses.pdf")
    
    except Exception as e:
        print(f"Error processing the uploaded PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=e)


@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    global global_data_context, global_data_type, sheets
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)

    global_data_context = ""  # Clear previous context if needed

    for file in files:
        try:
            global_file_loc = os.path.join(uploads_dir, file.filename)
            with open(global_file_loc, "wb") as buffer:
                buffer.write(await file.read())

            if file.filename.endswith('.pdf'):
                global_data_context += parse_ddq(global_file_loc, "uploads/parsedUpload.txt", True) + "\n"
                global_data_type = "pdf"
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
        except Exception as e:
            print(e)
            return {"message": f"Error processing file {file.filename}"}

    save_data_context()  # Save both the context and the data type
    return {"message": "Files uploaded and processed successfully"}


@app.post("/reset/")
def reset_data():
    global global_data_context, sheets
    global_data_context = ""  # Clear the global variable
    sheets = None
    
    # Remove the saved data file
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    return {"message": "Training data has been reset successfully"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)