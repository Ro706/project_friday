import os
import time
import threading
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "").strip('"')

# Prepare HTML
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>'''

# Save HTML
os.makedirs("data", exist_ok=True)
with open("data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Setup WebDriver
current_dir = os.getcwd()
Link = f"{current_dir}/data/Voice.html"
TempDirPath = os.path.join(current_dir, "frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress logs

# If you want headless mode uncomment this (but microphone won't work)
# chrome_options.add_argument("--headless")

# Start Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Utility functions
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "when", "where", "who", "which", "why", "whose", "whom",
        "where's", "what's", "how's", "who's", "when's", "why's",
        "can you", "could you", "would you", "should you", "is it possible to", "are you able to"
    ]

    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip('.!?') + "?"
    else:
        new_query = new_query.rstrip('.!?') + "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto")

def SpeechRecognition():
    driver.get("file:///" + Link)
    time.sleep(2)  # Give page time to load

    driver.find_element(By.ID, "start").click()
    time.sleep(2)

    collected_text = ""

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text and Text != collected_text:
                collected_text = Text
                driver.find_element(By.ID, "end").click()
                break
            time.sleep(0.5)
        except Exception as e:
            print("Error:", e)
            break

    if not collected_text.strip():
        driver.quit()
        return None

    driver.quit()

    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
        return QueryModifier(collected_text)
    else:
        SetAssistantStatus("Translating...")
        return QueryModifier(UniversalTranslator(collected_text))

def RunRecognitionInBackground():
    while True:
        result = SpeechRecognition()
        if result:
            print(f"[Recognized]: {result}")
        else:
            print("[No Speech Detected]")
        time.sleep(1)  # Delay before restarting

if __name__ == "__main__":
    # Run the recognition in a thread
    recognition_thread = threading.Thread(target=RunRecognitionInBackground)
    recognition_thread.start()
