from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Get the API key and username from environment variables
Username = env_vars.get("USERNAME", "").strip('"')
GroqAPIKey = env_vars.get("GROQ_API_KEY", "").strip('"')
Assistantname = "Jarvis"  # Define the assistant name

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

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Load chat messages if available
chat_log_path = r"data\ChatLog.json"
try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

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
        
        # Load previous messages
        with open(chat_log_path, "r") as f:
            messages = load(f)

        # Add user message
        messages.append({"role": "user", "content": query})

        # Get response
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
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
        messages.append({"role": "assistant", "content": Answer})

        # Save updated messages
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        # Modify the final answer and return
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # Clear chat log if error occurs
        with open(chat_log_path, "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Please try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = Chatbot(user_input)
        print(f"Chatbot: {response}")
