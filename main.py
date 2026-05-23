import speech_recognition as sr
import subprocess
import webbrowser   
import musiclyb
import requests
import os
import uuid
import winsound
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API key of groq loaded from environment
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

recognizer = sr.Recognizer()

recognizer.pause_threshold = 0.4
recognizer.non_speaking_duration = 0.3
newsapi = os.getenv("NEWS_API_KEY")

#whole speech function is to convert text to speech
def speak(text):

    filename = f"{uuid.uuid4()}.wav"

    
    venv_piper = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "piper.exe")
    piper_cmd = venv_piper if os.path.exists(venv_piper) else "piper"

    command = [
        piper_cmd,
        "--model",
        "voices/en_US-ryan-high.onnx",
        "--output_file",
        filename
    ]

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            text=True
        )

        process.communicate(text)

        winsound.PlaySound(filename, winsound.SND_FILENAME)
    except Exception as e:
        print(f"Error in speak function: {e}")

    try:
        os.remove(filename)

    except Exception as e:
        print(f"Error deleting file: {e}")
#funation to process the command given by the user and perform the corresponding action
def processcommand(c):
    if "open google" in c.lower():
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c.lower():
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in c.lower():
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1] 
        link = musiclyb.music[song]
        speak(f"Playing {song}")
        webbrowser.open(link)
    elif "news" in c.lower():
        speak("news goes like this!")
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        data = r.json()
        articles = data["articles"]
        for article in articles:
            speak(article["title"])
    else:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Jarvis, a smart AI assistant."
                },
                {
                    "role": "user",
                    "content": c
                }
            ],
            max_tokens=30
        )

        reply = response.choices[0].message.content

        print(reply)

        speak(reply)

if __name__ == "__main__":
    speak("Initializing Jarvis")
    with sr.Microphone() as source:
        print("Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            print("Listening...")
            try:
                # Wait and listen for the wake word "Jarvis" to activate the assistant
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
                word = recognizer.recognize_google(audio)

                if "jarvis" in word.lower().strip():
                    speak("yes sir")
                    print("Jarvis activated, listening for command...")  
                    
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    command = recognizer.recognize_google(audio)
                    print(f"Command: {command}")
                    processcommand(command) 
            except Exception as e:
                # If Google doesn't understand this error will pop up
                print(f"error: {e}")