from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values
from backend.Database import AddMessage, GetMessages, ClearChatLog, InitDB

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Get the API key and username from environment variables
Username = env_vars.get("USERNAME", "").strip('"')
GroqAPIKey = env_vars.get("GROQ_API_KEY", "").strip('"')
Assistantname = "Friday"  # Define the assistant name

# Initialize Database
InitDB()

# Initialize the Groq client correctly
try:
    client = Groq(api_key=GroqAPIKey)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

# Define the initial system prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System},
]

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%I")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = (
        f'Please use this real-time information if needed,\n'
        f'Today is {day}, {date} {month} {year}.\n'
        f'The current time is {hour}:{minute}:{second}.\n'
    )
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def Chatbot(query):
    global client
    try:
        if not client:
             # Try to re-initialize if it failed earlier (e.g. environment set later)
             client = Groq(api_key=GroqAPIKey)
        
        # Load previous messages from Database
        messages = GetMessages()

        # Add user message
        # messages.append({"role": "user", "content": query}) # Not needed to append here, we'll add to DB later

        # Get response
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages + [{"role": "user", "content": query}],
            max_completion_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean the answer
        Answer = Answer.replace("</s>", "")
        
        # Save updated messages to Database
        AddMessage("user", query)
        AddMessage("assistant", Answer)

        # Modify the final answer and return
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Clear chat log if error occurs
        ClearChatLog()
        return "An error occurred. Please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = Chatbot(user_input)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = Chatbot(user_input)
        print(f"Chatbot: {response}")
