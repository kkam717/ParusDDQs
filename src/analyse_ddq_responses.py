from openai import OpenAI
import os
from dotenv import load_dotenv

# Define the ConversationAgent class
class ConversationAgent:
    def __init__(self, model="gpt-4"):  # Changed to gpt-4 to match the script's usage
        self.model = model
        self.client = OpenAI()

    def continue_conversation(self, conversation, next_prompt):
        # Make the first API call
        response = self.client.chat.completions.create(model=self.model, messages=conversation)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=conversation
        )

        # Check if the response is incomplete
        if response.choices[0].finish_reason == 'length':
            conversation.append({'role': 'user', 'content': next_prompt})

            # Continue the conversation
            next_response = self.client.chat.completions.create(model=self.model, messages=conversation)

            return next_response.choices[0].message.content
        else:
            return response.choices[0].message.content


# Load environment variables and set up OpenAI client
load_dotenv()

# Function to get response from GPT-4
def get_gpt4_response(question):
    agent = ConversationAgent()

    system_message = "Analyse the following document, and extract all of the questions and answers in it. Any spillover for answers is labelled - append it to its given answer. Only return questions, labelled as they are in the original document, and answers, labelled as 'Answer:'. Ignore any lines labelled 'Skipped'.  Do not return any other text at all in your response, under any circumstance. "

    conversation = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
    ]
    next_prompt = ""

    response = agent.continue_conversation(conversation, next_prompt)
    print(2)

    return response

# Function to read questions from a text file
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Main function to execute the script
def main():
    print(1)
    file_path = 'DDQs/ddq_responses.txt'  # Path to your text file
    output_path = 'DDQs/analysed_responses.txt'
    try:
        response = get_gpt4_response(read_text_file(file_path))
        # print(response)
        with open(output_path, 'w') as file:
            file.write(str(response))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
