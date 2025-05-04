import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
from gtts import gTTS
import pygame
import os
import wikipedia
import tkinter as tk
from tkinter import scrolledtext
from custom_gui import create_main_window
from threading import Thread
import uuid
import pyautogui
import datetime
from dateutil import parser
import time
import socket
import sqlite3
import sys

# Declare global variables with default empty values
desktop_name = desktop_path = music_name = music_url = ""
webpage_name = webpage_url = newsapi = weatherapi = gemini_api = wake_word = ""

app_paths = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "word": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "vs code": r"C:\\Users\\ASUS\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
}
music = {
    "stealth": "https://www.youtube.com/watch?v=U47Tr9BB_wE",
    "march": "https://www.youtube.com/watch?v=Xqeq4b5u_Xw",
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI&pp=ygUHc2t5ZmFsbA%3D%3D",
    "wolf": "https://www.youtube.com/watch?v=ThCH0U6aJpU&list=PLnrGi_-oOR6wm0Vi-1OsiLiV5ePSPs9oF&index=21",
    "millionaire": "https://music.youtube.com/watch?v=yleXPEPJIgI",
}
url_dict = {
    "google": "https://google.com",
    "facebook": "https://facebook.com",
    "youtube": "https://youtube.com",
    "linkedin": "https://linkedin.com",
}

def main(email):
    global window, output_area, settings
    global desktop_name, desktop_path, music_name, music_url
    global webpage_name, webpage_url, newsapi, weatherapi, gemini_api, wake_word
    global app_paths, music, url_dict, genai

    # Fetch user-specific settings
    try:
        settings = fetch_settings(email)
    except Exception as e:
        print(f"Error: {e}")
        return

        # Now use these as Python variables
    desktop_name = settings["desktop_name"]
    desktop_path = settings["desktop_path"]
    music_name = settings["music_name"]
    music_url = settings["music_url"]
    webpage_name = settings["webpage_name"]
    webpage_url = settings["webpage_url"]
    newsapi = settings["news_api"]
    weatherapi = settings["weather_api"]
    gemini_api = settings["gemini_api"]
    wake_word = settings["wake_word"]

    # Update dynamic entries
    if desktop_name and desktop_path:
        app_paths[desktop_name] = desktop_path
    if music_name and music_url:
        music[music_name] = music_url
    if webpage_name and webpage_url:
        url_dict[webpage_name] = webpage_url

    import google.generativeai as genai
    genai.configure(api_key=gemini_api)

    # Test print (remove in production)
    print("Settings loaded:")
    print(settings)
    # UI and Assistant setup
    window, output_area = create_main_window(on_listen_click)
    speak("Initializing assistant...", output_area)
    Thread(target=listen_for_wake_word, daemon=True).start()
    window.mainloop()


def fetch_settings(email):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings WHERE email = ? ORDER BY id DESC LIMIT 1", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        (
            _id, email, gemini_api, weather_api, news_api, wake_word,
            webpage_name, webpage_url, desktop_name, desktop_path,
            music_name, music_url
        ) = row

        return {
            "email": email,
            "gemini_api": gemini_api,
            "weather_api": weather_api,
            "news_api": news_api,
            "wake_word": wake_word,
            "webpage_name": webpage_name,
            "webpage_url": webpage_url,
            "desktop_name": desktop_name,
            "desktop_path": desktop_path,
            "music_name": music_name,
            "music_url": music_url
        }
    else:
        raise Exception(f"No settings found for {email}.")


recognizer = sr.Recognizer()
engine = pyttsx3.init()
#newsapi = "confidential"
#weatherapi = "confidential"
# gemini_api = "confidential"

#wake_word = "python"  # Default wake word, can be changed dynamically

pygame.mixer.init()


app_paths[desktop_name] = desktop_path
music[music_name] = music_url
url_dict[webpage_name] = webpage_url


# Check if the system is connected to the internet
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

def speak(text, output_area, offline=False):
    try:
        if offline or not is_connected():
            if not offline:
                # Only announce once when switching to offline
                engine.say("No internet connection detected. Switching to offline mode.")
                engine.runAndWait()
            # Offline TTS using pyttsx3
            engine.say(text)
            engine.runAndWait()
        else:
            filename = f"temp_{uuid.uuid4()}.mp3"
            tts = gTTS(text)
            tts.save(filename)

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            output_area.insert(tk.END, f"{wake_word.capitalize()}: {text}\n")
            output_area.see(tk.END)

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(filename)
    except Exception as e:
        output_area.insert(tk.END, f"Error in speak: {e}\n")
        output_area.see(tk.END)
        print(f"Error in speak: {e}")


def aiProcess(command):
    try:
        if is_connected():
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(command)
            return response.text
        else:
            return "Error: No internet connection."
    except Exception as e:
        return f"Error with Gemini: {e}"

def get_weather(city, output_area, offline=False):
    try:
        if is_connected():
            url = f"http://api.weatherapi.com/v1/forecast.json?key={weatherapi}&q={city}&days=3"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                current = data["current"]
                forecast = data["forecast"]["forecastday"][0]["day"]
                condition = current["condition"]["text"]
                temp = current["temp_c"]
                max_temp = forecast["maxtemp_c"]
                min_temp = forecast["mintemp_c"]
                speak(f"The current weather in {city} is {condition} with {temp} degrees Celsius. "
                      f"Today's high is {max_temp} and the low is {min_temp}.", output_area)
            else:
                speak("I couldn't fetch the weather right now.", output_area)
        else:
            speak("Weather fetch is unavailable offline.", output_area)
    except Exception as e:
        speak(f"Weather fetch error: {e}", output_area)

def convert_to_math_expr(text):
    text = text.lower()
    text = text.replace("plus", "+").replace("minus", "-").replace("times", "*")
    text = text.replace("multiplied by", "*").replace("x", "*").replace("divided by", "/")
    text = text.replace("over", "/").replace("into", "*").replace("mod", "%")
    return text

def parse_time_string(time_str):
    try:
        clean_time = time_str.replace(".", "").upper().strip()
        return parser.parse(clean_time)
    except Exception:
        return None

def schedule_task(target_time, message, output_area):
    def wait_and_alert():
        now = datetime.datetime.now()
        delay = (target_time - now).total_seconds()
        if delay > 0:
            time.sleep(delay)
        speak(message, output_area)
    Thread(target=wait_and_alert, daemon=True).start()

def processCommand(c, output_area):
    c_lower = c.lower()
    if "remind me at" in c_lower or "set reminder at" in c_lower:
        try:
            parts = c.split("to")
            if len(parts) != 2:
                speak("Please include a message using 'to'.", output_area)
                return
            time_part = c_lower.split("at")[-1].split("to")[0].strip()
            reminder_msg = parts[1].strip()
            time_obj = parse_time_string(time_part)
            if not time_obj:
                speak("Sorry, I couldn't understand the reminder format.", output_area)
                return
            now = datetime.datetime.now()
            reminder_time = now.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
            if reminder_time < now: 
                reminder_time += datetime.timedelta(days=1)
            schedule_task(reminder_time, f"Reminder: {reminder_msg}", output_area)
            speak(f"Reminder set for {time_obj.strftime('%I:%M %p')}.", output_area)
        except Exception as e:
            speak(f"Error setting reminder: {e}", output_area)

    elif "weather in" in c_lower or "forecast in" in c_lower:
        try:
            city = c_lower.split("in")[-1].strip()
            get_weather(city, output_area)
        except Exception as e:
            speak(f"Could not process weather request: {e}", output_area)

    elif "set alarm for" in c_lower:
        try:
            time_part = c_lower.split("for")[-1].strip()
            time_obj = parse_time_string(time_part)
            if not time_obj:
                speak("Sorry, I couldn't understand the alarm time format.", output_area)
                return
            now = datetime.datetime.now()
            alarm_time = now.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
            if alarm_time < now:
                alarm_time += datetime.timedelta(days=1)
            schedule_task(alarm_time, "Wake up! This is your alarm.", output_area)
            speak(f"Alarm set for {time_obj.strftime('%I:%M %p')}.", output_area)
        except Exception as e:
            speak(f"Error setting alarm: {e}", output_area)
            
    elif c_lower.startswith("open"):
        name = c_lower.replace("open", "").strip()
        
        # Check if it's a website
        if name in url_dict:
            webbrowser.open(url_dict[name])
            speak(f"Opening {name.capitalize()}.", output_area)
        
        # Check if it's an application
        elif name in app_paths:
            try:
                os.startfile(app_paths[name])
                speak(f"Opening {name}.", output_area)
            except Exception as e:
                speak(f"Failed to open {name}: {e}", output_area)
        
        # If not found in either
        else:
            speak(f"Sorry, I don't know how to open {name}.", output_area)
        
    elif c_lower.startswith("play"):
        song = c_lower.split(" ", 1)[1]
        if song in music:
            link = music[song]
            webbrowser.open(link)
            speak(f"Playing {song}.", output_area)
        else:
            speak(f"Sorry, I don't have the song {song} in my library.", output_area)
    elif "pause music" in c_lower:
        pyautogui.press('space')
        speak("Pausing.", output_area)
    elif "resume music" in c_lower:
        pyautogui.press('space')
        speak("Resuming.", output_area)
    elif "today's news" in c_lower:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "ok":
                articles = data.get('articles', [])
                if articles:
                    speak("Here are some top headlines:", output_area)
                    for article in articles[:3]:
                        speak(article['title'], output_area)
                else:
                    speak("No news articles available at the moment.", output_area)
            else:
                speak(f"News API error: {data.get('message', 'Unknown error')}", output_area)
        else:
            speak("Failed to fetch news from the server.", output_area)
    elif "who is" in c_lower or "what is" in c_lower or "tell me about" in c_lower:
        try:
            if "who is" in c_lower:
                search_term = c_lower.replace("who is", "").strip()
            elif "what is" in c_lower:
                search_term = c_lower.replace("what is", "").strip()
            else:
                search_term = c_lower.replace("tell me about", "").strip()
            summary = wikipedia.summary(search_term, sentences=2)
            speak(summary, output_area)
        except wikipedia.exceptions.DisambiguationError:
            speak("That topic is a bit ambiguous. Please be more specific.", output_area)
        except wikipedia.exceptions.PageError:
            speak("I couldn't find anything on that topic.", output_area)
        except Exception as e:
            speak(f"Something went wrong while fetching info from Wikipedia: {e}", output_area)
    elif "calculate" in c_lower or "what is" in c_lower:
        try:
            expr = convert_to_math_expr(c_lower.replace("calculate", "").replace("what is", "").strip())
            result = eval(expr)
            speak(f"The answer is {result}", output_area)
        except Exception:
            speak("Sorry, I couldn't calculate that.", output_area)
    elif "create a file named" in c_lower:
        try:
            filename = c_lower.split("create a file named")[-1].strip()
            if not filename.endswith(".txt"):
                filename += ".txt"
            with open(filename, 'w') as f:
                f.write("")
            speak(f"File {filename} created.", output_area)
        except Exception as e:
            speak(f"Could not create file: {e}", output_area)

    elif "delete the file named" in c_lower:
        try:
            filename = c_lower.split("delete the file named")[-1].strip()
            if not filename.endswith(".txt"):
                filename += ".txt"
            if os.path.exists(filename):
                os.remove(filename)
                speak(f"File {filename} deleted.", output_area)
            else:
                speak(f"File {filename} does not exist.", output_area)
        except Exception as e:
            speak(f"Could not delete file: {e}", output_area)

    elif "search for file named" in c_lower:
        try:
            target = c_lower.split("search for file named")[-1].strip()
            if not target.endswith(".txt"):
                target += ".txt"
            found_paths = []
            for root, dirs, files in os.walk("."):
                if target in files:
                    found_paths.append(os.path.join(root, target))
            if found_paths:
                speak(f"Found {target} at {found_paths[0]}", output_area)
            else:
                speak(f"File {target} not found.", output_area)
        except Exception as e:
            speak(f"Could not search for file: {e}", output_area)

    elif "create a folder named" in c_lower:
        try:
            foldername = c_lower.split("create a folder named")[-1].strip()
            os.makedirs(foldername, exist_ok=True)
            speak(f"Folder {foldername} created.", output_area)
        except Exception as e:
            speak(f"Could not create folder: {e}", output_area)

    elif "delete the folder named" in c_lower:
        try:
            foldername = c_lower.split("delete the folder named")[-1].strip()
            if os.path.isdir(foldername):
                import shutil
                shutil.rmtree(foldername)
                speak(f"Folder {foldername} deleted.", output_area)
            else:
                speak(f"Folder {foldername} does not exist.", output_area)
        except Exception as e:
            speak(f"Could not delete folder: {e}", output_area)

    elif "read the file" in c_lower:
        try:
            filename = c_lower.split("read the file")[-1].strip()
            if not filename.endswith(".txt"):
                filename += ".txt"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                    if content:
                        speak(f"Here is the content of {filename}: {content}", output_area)
                    else:
                        speak(f"{filename} is empty.", output_area)
            else:
                speak(f"The file {filename} does not exist.", output_area)
        except Exception as e:
            speak(f"Could not read file: {e}", output_area)

    elif "take a screenshot" in c_lower:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            os.startfile(filename)  # Automatically opens the screenshot
            speak(f"Screenshot taken and saved as {filename}.", output_area)
        except Exception as e:
            speak(f"Could not take screenshot: {e}", output_area)

    elif "lock the system" in c_lower:
        try:
            speak("Locking the system.", output_area)
            os.system("rundll32.exe user32.dll,LockWorkStation")
        except Exception as e:
            speak(f"Failed to lock the system: {e}", output_area)

    elif c_lower == "close assistant":
        speak("Closing assistant.", output_area)
        window.destroy()
    else:
        output = aiProcess(c)
        speak(output, output_area)

def listen_for_wake_word():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                word = recognizer.recognize_google(audio) if is_connected() else recognizer.recognize_sphinx(audio)
                if word.lower() == wake_word.lower():
                    Thread(target=speak, args=("Yes?", output_area, not is_connected()), daemon=True).start()
                    
                    print("Listening for command...")
                    audio2 = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio2) if is_connected() else recognizer.recognize_sphinx(audio2)

                    window.after(0, lambda: output_area.insert(tk.END, f"Command: {command}\n"))
                    window.after(0, lambda: processCommand(command, output_area))

            except Exception as e:
                print(f"Error: {e}")
                continue

def on_listen_click():
    def listen_thread():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                speak("Listening...", output_area, offline=not is_connected())
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio) if is_connected() else recognizer.recognize_sphinx(audio)
                output_area.insert(tk.END, f"Command: {command}\n")
                processCommand(command, output_area)
            except:
                speak("Sorry, I couldn't understand.", output_area)

    Thread(target=listen_thread, daemon=True).start()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test.py <email>")
        sys.exit(1)

    user_email = sys.argv[1]
    main(user_email)
