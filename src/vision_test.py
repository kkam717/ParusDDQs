import fitz  # PyMuPDF
import base64
import requests
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
from tqdm import tqdm

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def save_pages_as_pngs(pdf_path: str, output_folder: str):
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        zoom_x = 3.0
        zoom_y = 3.0
        mat = fitz.Matrix(zoom_x, zoom_y)
        
        pixmap = page.get_pixmap(matrix=mat)
        
        image_path = os.path.join(output_folder, f'{os.path.basename(pdf_path).replace(".pdf", "")}_page_{page_num + 1}.png')
        pixmap.save(image_path)

def encode_image_to_base64(image_path: str):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4_with_image(base64_image, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Consider the following image. If you detect a table in this image, extract the elements of the table in a question and answer format and return them, labelling them with the question number that is on the document. If the question section of the table (left) is blank, assume it is spillover from a previous question, and set the question name to 'Spillover:'. If you do not detect a table, return 'Skipped'. Do not under any circumstance return anything other than a question number with an answer, spillover or 'Skipped'. "
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    while True:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 429:  # Rate limit exceeded
            error_info = response.json().get('error', {})
            wait_time = float(error_info.get('message', '').split(' ')[-2])
            time.sleep(wait_time or retry_delay)
            continue  # Retry the request
        return response.json()['choices'][0]['message']['content']

def main():
    pdf_directory = 'DDQs'  # Directory containing the PDF files
    output_text_file = 'DDQs/ddq_responses.txt'
    output_folder = 'DDQs/output_images'  # Directory to store output images
    api_key = os.getenv('OPENAI_API_KEY')  # Load API key from .env file

    if not api_key:
        raise ValueError("API key not found in .env file")

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(output_text_file, 'w') as file:

        # List all PDF files in the specified directory
        pdf_paths = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        for pdf_path in pdf_paths:
            save_pages_as_pngs(pdf_path, output_folder)

            image_files = sorted([f for f in os.listdir(output_folder) if f.endswith(".png") and os.path.basename(pdf_path).replace(".pdf", "") in f], key=lambda x: int(x.split('_page_')[1].split('.png')[0]))

            pbar = tqdm(total=len(image_files))
            for image_file in image_files:
                image_path = os.path.join(output_folder, image_file)
                base64_image = encode_image_to_base64(image_path)
                response = call_gpt4_with_image(base64_image, api_key)
                file.write(str(response) + "\n\n")
                pbar.update(n=1)
            
            for i in os.listdir(output_folder):
                os.remove(image_path)
            

if __name__ == "__main__":
    main()
