from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import playonyt, search
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
try:
    from TextToSpeech import speak
except ImportError:
    from backend.TextToSpeech import speak
import wikipedia
import pyautogui
from pycaw.pycaw import AudioUtilities

# Load environment variables
env_vars = dotenv_values(".env")
GROQ_API_KEY = env_vars.get("GROQ_API_KEY", "").strip('"')
OPENWEATHER_API_KEY = env_vars.get("OPENWEATHER_API_KEY", "").strip('"')

# Instantiate Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

def GoogleSearch(query):
    print(f"[bold green]Searching Google for: {query}[/bold green]")
    search(query)
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return query

def YouTubeSearch(query):
    print(f"[bold green]Searching YouTube for: {query}[/bold green]")
    playonyt(query)
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return query

def OpenWebsite(url):
    print(f"[bold green]Opening: {url}[/bold green]")
    webbrowser.open(url)
    return url

def CloseApp(app_name):
    print(f"[bold green]Closing: {app_name}[/bold green]")
    close(app_name)
    return app_name

def OpenApp(app_name):
    print(f"[bold green]Opening: {app_name}[/bold green]")
    
    # Common websites mapping
    websites = {
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "whatsapp": "https://web.whatsapp.com"
    }
    
    if app_name.lower() in websites:
        webbrowser.open(websites[app_name.lower()])
        return app_name

    # If not a known website, try AppOpener
    try:
        # appopen might return "NOT FOUND" or just print it.
        # Check AppOpener documentation for return values if needed.
        appopen(app_name, match_closest=True)
    except Exception as e:
        print(f"AppOpener failed: {e}")
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        
    return app_name

def contentWrite(query):
    if not groq_client:
        print("[bold red]Groq client not initialized.[/bold red]")
        return "Content generation unavailable."
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        result_content = response.choices[0].message.content.strip()

        if not result_content:
            print("[bold red]No content generated.[/bold red]")
            return "No content generated."

        print(result_content)
        filepath = os.path.abspath("content.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result_content)
        subprocess.Popen(["notepad.exe", filepath])

        return result_content

    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        return f"Error: {e}"


def TakeScreenshot(filename="screenshot.png"):
    try:
        filepath = os.path.abspath(filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        print(f"[bold green]Screenshot saved at {filepath}[/bold green]")
        return filepath
    except Exception as e:
        print(f"[bold red]Screenshot Error:[/bold red] {e}")
        return f"Error: {e}"

def GetWeather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            raise Exception(response.get("message", "Unknown error"))
        weather = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        result = f"Weather in {city}: {weather}, Temperature: {temp}°C"
        print(f"[bold blue]{result}[/bold blue]")
        speak(result)
        return result
    except Exception as e:
        print(f"[bold red]Weather Error:[/bold red] {e}")
        return f"Error: {e}"

def GetNews():
    try:
        rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        xml = requests.get(rss_url).text
        soup = BeautifulSoup(xml, "xml")
        headlines = [item.title.text for item in soup.find_all("item")[:5]]
        for i, h in enumerate(headlines, 1):
            print(f"[bold yellow]{i}. {h}[/bold yellow]")
            speak(h)
        return headlines
    except Exception as e:
        print(f"[bold red]News Error:[/bold red] {e}")
        return []

def TellJoke():
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?type=single").json()
        joke = response.get("joke", "Couldn't fetch a joke.")
        print(f"[italic green]Joke: {joke}[/italic green]")
        speak(joke)
        return joke
    except Exception as e:
        print(f"[bold red]Joke Error:[/bold red] {e}")
        return f"Error: {e}"

def WikiSummary(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        print(f"[bold magenta]Wikipedia Summary:[/bold magenta] {summary}")
        speak(summary)
        return summary
    except Exception as e:
        print(f"[bold red]Wikipedia Error:[/bold red] {e}")
        return f"Error: {e}"

def VolumeControl(action, step=0.1):
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume

        current = volume.GetMasterVolumeLevelScalar()

        if action == "volume up":
            volume.SetMasterVolumeLevelScalar(min(1.0, current + step), None)
            print("Volume Increased")

        elif action == "volume down":
            volume.SetMasterVolumeLevelScalar(max(0.0, current - step), None)
            print("Volume Decreased")

        elif action == "mute":
            volume.SetMute(1, None)
            print("Muted")

        elif action == "unmute":
            volume.SetMute(0, None)
            print("Unmuted")

    except Exception as e:
        print("Volume Control Error:", e)

def SystemCommand(cmd):
    cmd = cmd.lower()
    try:
        if "shutdown" in cmd:
            os.system("shutdown /s /t 1")
        elif "restart" in cmd:
            os.system("shutdown /r /t 1")
        elif "sleep" in cmd:
            # This command might hibernate if hibernation is enabled. 
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif "log off" in cmd or "sign out" in cmd:
            os.system("shutdown /l")
        
        print(f"[bold green]Executed system command: {cmd}[/bold green]")
    except Exception as e:
        print(f"[bold red]System Command Error:[/bold red] {e}")

def CreateFolder(folder_name):
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            path = os.path.abspath(folder_name)
            print(f"[bold green]Folder created: {path}[/bold green]")
            return f"Folder '{folder_name}' created at {path}"
        else:
            path = os.path.abspath(folder_name)
            print(f"[bold yellow]Folder already exists: {path}[/bold yellow]")
            return f"Folder '{folder_name}' already exists at {path}"
    except Exception as e:
        print(f"[bold red]Create Folder Error:[/bold red] {e}")
        return f"Error creating folder: {e}"


# Example usage
if __name__ == "__main__":
    # content = contentWrite("write research paper for block chain and AI")
    # print(f"Chatbot: {content}")

    # Uncomment to try features:
    GoogleSearch("ChatGPT vs Gemini")
    # YouTubeSearch("AI in 2025")
    # GetWeather("Delhi")
    # GetNews()
    # TellJoke()
    # WikiSummary("Large Language Model")
    # SystemCommand("restart")
    # TakeScreenshot("test_screenshot.png")
    # SystemCommand("restart")
    # VolumeControl("increase")
    # VolumeControl("increase")
    # VolumeControl("increase")
    # VolumeControl("decrease")
    # VolumeControl("mute")
    # VolumeControl("unmute")