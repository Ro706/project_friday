import os
# Suppress pygame support message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import threading
import subprocess
from dotenv import load_dotenv

# Add subdirectories to path if necessary
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

# Import backend modules
from backend.Model import FirstLayerDMM
from backend.Chatbot import Chatbot
from backend.RealtimeSearchEngine import RealtimeInformation
from backend.Automation import (
    OpenApp, CloseApp, GoogleSearch, YouTubeSearch, 
    contentWrite, SystemCommand, VolumeControl, TakeScreenshot,
    CreateFolder
)
from backend.Features import ShowFeatures
from backend.ImageGeneration import GenerateImage
from backend.TextToSpeech import speak

# Import core modules
from core.news import news_report
from core.weather import tellmeTodaysWeather
from core.cpu_info import cpu_info
from core.ram_info import RamInfo
from core.PhotoCaptureApp import create_gui
from core.mail import send_mail

# Import game modules
import game1
import game2

# Load environment variables
load_dotenv()
USERNAME = os.getenv("USERNAME", "User")

def handle_game_selection():
    """Handles interactive game selection when no game is specified."""
    msg = "Which game would you like to play? 1. Tic Tac Toe, 2. Ball Bouncing"
    print(f"Friday: {msg}")
    speak(msg)
    
    choice = input(f"[{USERNAME}]: ").strip().lower()
    if "1" in choice or "tic" in choice:
        speak("Starting Tic Tac Toe.")
        game1.game()
    elif "2" in choice or "ball" in choice:
        speak("Starting Ball Bouncing Game.")
        game2.start_game()
    else:
        err_msg = "Invalid selection. Please try again with a game name or number."
        print(f"Friday: {err_msg}")
        speak(err_msg)

def execute_task(task_query, original_prompt):
    """Executes a single task based on the classified query."""
    print(f"\n[Executing Task]: {task_query}")
    
    # Handle literal "(query)" or missing query text from Model.py
    def clean_query(prefix, text):
        q = text.replace(prefix, "").strip()
        if not q or q == "(query)":
            return original_prompt
        return q

    if task_query.startswith("general"):
        query = clean_query("general", task_query)
        response = Chatbot(query)
        print(f"Friday: {response}")
        speak(response)

    elif task_query.startswith("realtime"):
        query = clean_query("realtime", task_query)
        if "news" in query.lower():
            response = news_report()
            print(f"Friday: {response}")
        elif "weather" in query.lower():
            response = tellmeTodaysWeather()
            print(f"Friday: {response}")
        elif "cpu" in query.lower():
            response = cpu_info()
            print(f"Friday: {response}")
            speak(f"Here is your CPU information: {response}")
        elif "ram" in query.lower():
            response = RamInfo().info()
            print(f"Friday: {response}")
            speak(response)
        else:
            response = RealtimeInformation(query)
            print(f"Friday: {response}")
            speak(response)

    elif task_query.startswith("open"):
        app_name = clean_query("open", task_query)
        if "photo" in app_name.lower() or "camera" in app_name.lower():
            speak("Opening camera.")
            create_gui()
        elif "game" in app_name.lower():
            if "tic tac toe" in app_name.lower() or "1" in app_name.lower():
                speak("Starting Tic Tac Toe.")
                game1.game()
            elif "ball" in app_name.lower() or "2" in app_name.lower():
                speak("Starting Ball Bouncing Game.")
                game2.start_game()
            else:
                handle_game_selection()
        else:
            OpenApp(app_name)
            speak(f"Opening {app_name}.")

    elif task_query.startswith("close"):
        app_name = clean_query("close", task_query)
        CloseApp(app_name)
        speak(f"Closing {app_name}.")

    elif task_query.startswith("play"):
        song_name = clean_query("play", task_query)
        if "spotify" in song_name.lower():
            OpenApp("https://open.spotify.com/")
            speak("Opening Spotify.")
        else:
            YouTubeSearch(song_name)
            speak(f"Playing {song_name} on YouTube.")

    elif task_query.startswith("generate image"):
        prompt = clean_query("generate image", task_query)
        speak("Generating images, please wait.")
        GenerateImage(prompt)

    elif task_query.startswith("system"):
        cmd = clean_query("system", task_query)
        if cmd in ["mute", "unmute", "volume up", "volume down"]:
            VolumeControl(cmd)
        elif cmd in ["screenshot", "take screenshot"]:
            TakeScreenshot()
            speak("Screenshot taken.")
        elif cmd in ["features", "help", "menu"]:
            ShowFeatures()
            speak("Here are the features I can perform.")
        else:
            SystemCommand(cmd)

    elif task_query.startswith("content"):
        topic = clean_query("content", task_query)
        speak(f"Writing content about {topic}.")
        contentWrite(topic)

    elif task_query.startswith("google search"):
        topic = clean_query("google search", task_query)
        GoogleSearch(topic)
        speak(f"Searching Google for {topic}.")

    elif task_query.startswith("youtube search"):
        topic = clean_query("youtube search", task_query)
        YouTubeSearch(topic)
        speak(f"Searching YouTube for {topic}.")

    elif task_query.startswith("game"):
        game_name = clean_query("game", task_query)
        if "tic tac toe" in game_name or "1" in game_name:
            speak("Starting Tic Tac Toe.")
            game1.game()
        elif "ball" in game_name or "2" in game_name:
            speak("Starting Ball Bouncing Game.")
            game2.start_game()
        else:
            handle_game_selection()

    elif task_query.startswith("mail"):
        speak("Preparing to send an email.")
        send_mail()

    elif task_query.startswith("create folder"):
        folder_name = clean_query("create folder", task_query)
        result = CreateFolder(folder_name)
        # print(f"Friday: {result}") # result already has "Folder '...' created at ..."
        speak(result)

    elif task_query == "exit":
        speak("Goodbye! Have a nice day.")
        sys.exit()

def main():
    msg = f"Hello {USERNAME}, I am Friday. How can I help you today?"
    print(f"\n[Friday]: {msg}")
    speak(msg)

    while True:
        # Get Text Input
        query = input(f"\n[{USERNAME}]: ").strip()
        
        if not query:
            continue

        # Classify query
        tasks = FirstLayerDMM(query)
        
        # Execute tasks
        for task in tasks:
            execute_task(task, query)

if __name__ == "__main__":
    main()
