import os
import signal
import webbrowser
import pyjokes
from backend.TextToSpeech import speak
import speech_recognition as sr
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import spacy
from textblob import TextBlob
from transformers import pipeline
from core.PhotoCaptureApp import create_gui
from core.ram_info import RamInfo
from core.cpu_info import cpu_info
from core.weather import tellmeTodaysWeather
from core.news import news_report
from core.wishme import wish_me
from core.mail import send_mail
from game.game1 import game

load_dotenv()

# Load SpaCy model for NLP
nlp = spacy.load("en_core_web_sm")

# Load sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"

# Load question-answering pipeline for contextual understanding
qa_pipeline = pipeline("question-answering")

def answer_question(context, question):
    result = qa_pipeline(question=question, context=context)
    return result['answer']

def signal_handler(sig, frame):
    print("Goodbye, Have a nice day!")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

class FileManager:
    def __init__(self, base_path="."):
        self.base_path = os.path.abspath(base_path)

    def create_file(self, filename, content=""):
        path = os.path.join(self.base_path, filename)
        with open(path, "w") as file:
            file.write(content)
        return f"File created: {path}"

    def read_file(self, filename):
        path = os.path.join(self.base_path, filename)
        if os.path.exists(path):
            with open(path, "r") as file:
                return file.read()
        return f"File not found: {path}"

    def append_to_file(self, filename, content):
        path = os.path.join(self.base_path, filename)
        if os.path.exists(path):
            with open(path, "a") as file:
                file.write(content)
            return f"Content appended to: {path}"
        return f"File not found: {path}"

    def delete_file(self, filename):
        path = os.path.join(self.base_path, filename)
        if os.path.exists(path):
            os.remove(path)
            return f"File deleted: {path}"
        return f"File not found: {path}"

    def create_directory(self, dirname):
        path = os.path.join(self.base_path, dirname)
        os.makedirs(path, exist_ok=True)
        return f"Directory created: {path}"

    def delete_directory(self, dirname):
        path = os.path.join(self.base_path, dirname)
        if os.path.exists(path) and os.path.isdir(path):
            try:
                os.rmdir(path)
                return f"Directory deleted: {path}"
            except OSError as e:
                return f"Error: Could not delete {path}. The directory might not be empty."
        return f"Directory not found: {path}"

    def search_file(self, filename, start_path="."):
        start_path = os.path.abspath(start_path)
        for root, _, files in os.walk(start_path):
            if filename in files:
                return f"File found: {os.path.join(root, filename)}"
        return f"File not found: {filename}"

    def list_directory(self, dirname="."):
        path = os.path.join(self.base_path, dirname)
        if os.path.exists(path) and os.path.isdir(path):
            files = os.listdir(path)
            return f"Contents of {path}:\n" + "\n".join(files) if files else f"Directory {path} is empty"
        return f"Directory not found: {path}"

class RecognizeSpeech:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.pause_threshold = 1
            audio = self.recognizer.listen(source)

        try:
            print("Recognizing...")
            query = self.recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query.lower()
        except Exception as e:
            print(e)
            print("Say that again please...")
            return "none"

class Speak:
    def __init__(self):
        pass

    def speak(self, text):
        print(f"Jarvis: {text}")
        speak(text)

class Bard:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def chat(self, query):
        try:
            query = f"Your name is Jarvis, our intelligent and reliable personal assistant. Try to give each response in 3 to 4 lines. {query}"
            response = self.model.generate_content(query)
            return response.text.replace("*", "").replace("**", "") if response and hasattr(response, "text") else "Sorry, I could not understand that."
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return "Sorry, I encountered an error while processing your request."

def extract_intent_and_entities(query):
    doc = nlp(query)
    intent = None
    entities = []

    for token in doc:
        if token.dep_ == "ROOT":
            intent = token.lemma_
        if token.ent_type_:
            entities.append((token.text, token.ent_type_))

    # Post-process time entities to ensure correct formatting
    for i, (entity, label) in enumerate(entities):
        if label == "TIME":
            # Normalize time format
            time_str = entity.lower().replace(".", "").replace("am", " AM").replace("pm", " PM")
            try:
                # Parse the time string to a datetime object
                time_obj = datetime.strptime(time_str, "%I:%M %p")
                # Format it back to a standardized format
                entities[i] = (time_obj.strftime("%I:%M %p"), label)
            except ValueError:
                # If parsing fails, keep the original entity
                pass

    return intent, entities

def get_user_input(speaker, speech_recognizer, prompt):
    speaker.speak(prompt)
    user_input = speech_recognizer.listen()
    if user_input == "none":
        speaker.speak("I didn't catch that. Please try again.")
        user_input = speech_recognizer.listen()
    return user_input

def main():
    speaker = Speak()
    speech_recognizer = RecognizeSpeech()
    file_manager = FileManager()
    user_name = "Rohit"

    wish_me(user_name)

    context = ""  # To maintain conversation context

    while True:
        query = speech_recognizer.listen()
        if query == "none":
            continue

        intent, entities = extract_intent_and_entities(query)
        print(f"Intent: {intent}, Entities: {entities}")

        sentiment = analyze_sentiment(query)
        print(f"Sentiment: {sentiment}")

        if 'exit' in query or 'goodbye' in query:
            speaker.speak("Goodbye, Have a nice day!")
            break
        elif intent in ['open', 'search'] and 'youtube' in query:
            speaker.speak("Opening Youtube")
            webbrowser.open("youtube.com")
        elif intent in ['open', 'search'] and 'google' in query:
            speaker.speak("Opening Google")
            query = query.replace("open google and search for", "")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        elif intent in ['open', 'search'] and 'stackoverflow' in query:
            speaker.speak("Opening Stackoverflow")
            webbrowser.open("stackoverflow.com")
        elif intent in ['open', 'search'] and 'github' in query:
            speaker.speak("Opening Github")
            webbrowser.open("github.com")
        elif intent in ['open', 'search'] and 'facebook' in query:
            speaker.speak("Opening Facebook")
            webbrowser.open("facebook.com")
        elif intent in ['open', 'search'] and 'instagram' in query:
            speaker.speak("Opening Instagram")
            webbrowser.open("instagram.com")
        elif 'ram' in query:
            speaker.speak("Here are the RAM details:")
            ram_info = RamInfo().info()
            speaker.speak(ram_info)
        elif "play music" in query:
            os.system("spotify")
        elif 'cpu' in query:
            cpu_details = cpu_info()
            speaker.speak("Here are the CPU details:")
            speaker.speak(cpu_details)
        elif 'weather' in query:
            speaker.speak("Here is the weather in Nagpur:")
            tellmeTodaysWeather()
        elif "joke" in query:
            joke = pyjokes.get_joke()
            print(joke)
            speaker.speak(joke)
        elif 'time' in query:
            speaker.speak("The current time is:")
            speaker.speak(datetime.now().strftime("%H:%M:%S"))
        elif 'create file' in query or 'make file' in query:
            filename = input("Please Enter file name: ")
            os.system(f"echo. > {filename}")
            print("File created successfully")
        elif 'read file' in query:
            filename = query.split("file")[-1].strip() or input("Please Enter file name: ")
            if filename != "none":
                content = file_manager.read_file(filename)
                speaker.speak(f"Content of {filename}:")
                speaker.speak(content)
            else:
                speaker.speak("Sorry, I couldn't read the file without a name.")
        elif 'append to file' in query or 'add to file' in query:
            filename = query.split("file")[-1].strip() or input("Which file would you like to append to?")
            content = get_user_input(speaker, speech_recognizer, "What content should I append to the file?")
            if filename != "none" and content != "none":
                try:
                    result = file_manager.append_to_file(filename, content)
                    speaker.speak(result)
                except Exception as e:
                    speaker.speak(f"Error appending to file: {e}")
            else:
                speaker.speak("Sorry, I couldn't append to the file due to missing information.")
        elif 'delete file' in query or 'remove file' in query:
            filename = query.split("file")[-1].strip() or input("Enter file name: ")
            if filename != "none":
                confirmation = input(f"Are you sure you want to delete {filename}? Say yes to confirm.")
                if confirmation == "yes":
                    result = file_manager.delete_file(filename)
                    speaker.speak(result)
                else:
                    speaker.speak("File deletion cancelled.")
            else:
                speaker.speak("Sorry, I couldn't delete the file without a name.")
        elif 'create directory' in query or 'create folder' in query or 'add folder' in query:
            dirname = query.split("directory")[-1].strip() or query.split("folder")[-1].strip() or input("What should I name the directory or folder?")
            if dirname != "none":
                result = file_manager.create_directory(dirname)
                print("Directory created:", result)
            else:
                speaker.speak("Sorry, I couldn't create the directory without a name.")
        elif 'delete directory' in query or 'delete folder' in query or 'remove folder' in query:
            dirname = query.split("directory")[-1].strip() or query.split("folder")[-1].strip() or input("Which directory or folder would you like me to delete?")
            if dirname != "none":
                confirmation = input(f"Are you sure you want to delete the directory {dirname}? Say yes to confirm.")
                if confirmation == "yes":
                    result = file_manager.delete_directory(dirname)
                    speaker.speak(result)
                else:
                    speaker.speak("Directory deletion cancelled.")
            else:
                speaker.speak("Sorry, I couldn't delete the directory without a name.")
        elif 'list directory' in query or 'list folder' in query:
            dirname = query.split("directory")[-1].strip() or query.split("folder")[-1].strip() or input("Which directory or folder would you like me to list? Say current for the current directory.")
            if dirname == "current":
                dirname = "."
            if dirname != "none":
                result = file_manager.list_directory(dirname)
                speaker.speak(result)
            else:
                speaker.speak("Listing current directory:")
                result = file_manager.list_directory(".")
                speaker.speak(result)
        elif 'search file' in query or 'find file' in query:
            filename = query.split("file")[-1].strip() or get_user_input(speaker, speech_recognizer, "What file would you like me to search for?")
            if filename != "none":
                speaker.speak(f"Searching for file {filename}...")
                result = file_manager.search_file(filename)
                speaker.speak(result)
            else:
                speaker.speak("Sorry, I couldn't search without a file name.")
        elif "news report" in query:
            news_report()
        elif "mail" in query:
            send_mail()
        elif "game" in query:
            speaker.speak("Opening a game for you!")
            game()
        elif "selfie" in query:
            speaker.speak("Taking a selfie for you!")
            create_gui()
        elif "question" in intent:
            # Use contextual understanding to answer questions
            answer = answer_question(context, query)
            speaker.speak(answer)
            context = query  # Update context with the latest query
        else:
            response = Bard().chat(query)
            speaker.speak(response)

if __name__ == "__main__":
    main()
