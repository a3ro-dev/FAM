import libs.gpt as gpt
import random
import subprocess
import time
import cv2
from gtts import gTTS
import speech_recognition as sr
from functools import lru_cache
import pyaudio
import threading
import yaml
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pyttsx3

# Load configuration
with open('conf/config.yaml') as file:
    config = yaml.safe_load(file)

emailID = config['utilities']['email']['sender_email']
emailPasswd = config['utilities']['email']['sender_password']
imgPath = config['utilities']['image_path']
author = config['utilities']['author']
success = config['utilities']['audio_files']['success']
error = config['utilities']['audio_files']['error']
load = config['utilities']['audio_files']['load']
newsAPI = config['utilities']['news_api_key']
weatherAPI = config['utilities']['weather_api_key']

Gpt = gpt.Generation()

class Utilities:
    """
    Utilities for the app
    """

    def __init__(self):
        self.author = author    
        self.audio_files = {
            "success": success,
            "error": error,
            "load": load
        }

    def playChime(self, type: str):
        try:
            if type in self.audio_files:
                subprocess.run(["aplay", self.audio_files[type]], check=True)
            else:
                raise ValueError(f"Unknown chime type: {type}")
        except Exception as e:
            print(f"Error in playChime: {e}")
    
    def speak(self, text: str):
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            print(text)
        except Exception as e:
            print(f"Error in speak: {e}")

    def getSpeech(self):
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening for speech...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source)
            text = r.recognize(audio)  # Use recognize_google for speech recognition
            print(f"Recognized speech: {text}")
            self.playChime('success')
        except Exception as e:
            self.playChime('error')
            print(f"Error in getSpeech: {e}")
        return str(text)
    
    def getTime(self):
        return time.ctime()

    def getDate(self):
        now = datetime.now()
        day = now.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return now.strftime(f"%B {day}{suffix}, %Y")

    @lru_cache(maxsize=32)
    def getWeather(self, city: str, api_key=weatherAPI):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for key in ["temp", "feels_like", "temp_min", "temp_max"]:
                data["main"][key] -= 273.15

            finalData = {
                "weather_condition": data["weather"][0]["main"],
                "detailed_condition": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "pressure": data["main"]["pressure"],
                "humidity": data["main"]["humidity"],
                "visibility": data["visibility"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "cloudiness": data["clouds"]["all"],
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
                "location": data["name"],
            }
            return Gpt.generate_text_response(f"Given the following weather data: {finalData}, generate a concise and informative weather report.")
        except requests.exceptions.RequestException as e:
            print(f"Error in getWeather: {e}")
            return None
        except Exception as e:
            print(f"Error in getWeather: {e}")
            return None
        
    @lru_cache(maxsize=32)
    def getNews(self, api_key=newsAPI, num_articles=5):
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if len(articles) < num_articles:
                raise Exception(f"Only {len(articles)} articles available, cannot select {num_articles}")
            
            selected_articles = random.sample(articles, num_articles)
    
            newsList = []
            for article in selected_articles:
                news = Gpt.generate_text_response(f"Summarize the given article in a journalistic style, focusing on the key points and events. Please avoid including any hyperlinks.\n{article}")
                self.playChime('success')
                newsList.append(news)
    
            return newsList
        except requests.exceptions.RequestException as e:
            self.playChime('error')
            print(f"Error in getNews: {e}")
            return []
        except Exception as e:
            self.playChime('error')
            print(f"Error in getNews: {e}")
            return []

    def get_part_of_day(self):
        current_hour = datetime.now().hour
    
        if current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 20:
            return "evening"
        else:
            return "night"
    
    def startMyDay(self, location='Allahabad'):
        try:
            part_of_day = self.get_part_of_day()
            self.speak(f"Good {part_of_day}!")
            self.speak(f"Today is {self.getDate()}")
            self.speak(f"The current time is {self.getTime()}")
    
            weather_report = self.getWeather(location)
            if weather_report:
                self.speak(str(weather_report))
            else:
                self.speak(f"Sorry, I couldn't fetch the weather for {location}")
    
            news_headlines = self.getNews()
            if news_headlines:
                self.speak("Here are today's top news headlines.")
                for news in news_headlines:
                    self.speak(news)
            else:
                self.speak("Sorry, I couldn't fetch the news headlines.")
    
            self.speak(f"That's all for now. Have a great {part_of_day}!")
        except Exception as e:
            self.speak(f"Sorry, I encountered an error: {e}")

    def send_email(self, recipient: str, subject: str, content: str):
        sender_email = emailID
        sender_password = emailPasswd
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject

        body = f"{content}\n\nSent from FAM ASSISTANT"
        message.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")

    def captureImage(self, save_path=imgPath):
        try:
            time.sleep(1)
            
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                self._handle_camera_error("Failed to open camera")
            
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
            ret, frame = camera.read()
            if not ret:
                self._handle_camera_error("Failed to capture image")
    
            cv2.imwrite(save_path, frame)
            self.playChime('success')
        except Exception as e:
            self.playChime('error')
            print(f"Error in captureImage: {e}")
        finally:
            camera.release()
            cv2.destroyAllWindows()

    def _handle_camera_error(self, message: str):
        self.playChime('error')
        raise Exception(message)