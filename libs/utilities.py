import libs.gpt as gpt
import random
import time
import cv2
import speech_recognition as sr
from functools import lru_cache
import yaml
import requests
import shutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import openai
import subprocess
from pydub import AudioSegment  # type: ignore
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
openai.api_key = config['main']['openai_api_key']

class Utilities:
    def __init__(self):
        self.author = author    
        self.audio_files = {
            "success": success,
            "error": error,
            "load": load
        }
        logging.info("Utilities class initialized.")

    def playChime(self, type: str):
        try:
            if type in self.audio_files:
                logging.debug(f"Playing chime of type: {type}")
                subprocess.run(['ffplay', '-nodisp', '-autoexit', self.audio_files[type]], check=True)
            else:
                raise ValueError(f"Unknown chime type: {type}")
        except Exception as e:
            logging.error(f"Error in playChime: {e}")

    def speak(self, text: str):
        try:
            logging.debug(f"Generating speech for text: {text}")
            response = openai.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input=text,
            )
            save_file_path = f"/home/pi/FAM/assets/cache/{uuid.uuid4()}.mp3"
            response.stream_to_file(save_file_path)
            logging.info(f"{save_file_path}: A new audio file was saved successfully!")
            subprocess.run(['ffplay', '-nodisp', '-autoexit', save_file_path], check=True)
        except Exception as e:
            logging.error(f"Error in speak: {e}")

    def getSpeech(self):
        if not shutil.which("flac"):
            logging.error("FLAC conversion utility not available. Please install FLAC.")
            return ""
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                logging.info("Listening for speech...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source)
            text = r.recognize(audio)
            logging.info(f"Recognized speech: {text}")
            self.playChime('success')
            return text
        except Exception as e:
            self.playChime('error')
            logging.error(f"Error in getSpeech: {e}")
            return ""

    def getTime(self):
        current_time = time.ctime()
        logging.info(f"Current time: {current_time}")
        return current_time

    def getDate(self):
        now = datetime.now()
        day = now.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        current_date = now.strftime(f"%B {day}{suffix}, %Y")
        logging.info(f"Current date: {current_date}")
        return current_date

    @lru_cache(maxsize=32)
    def getWeather(self, city: str, api_key=weatherAPI):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}"
        try:
            logging.debug(f"Fetching weather data for city: {city}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for key in {"temp", "feels_like", "temp_min", "temp_max"}:
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
            logging.debug(f"Weather data: {finalData}")
            return Gpt.generate_text_response(f"Given the following weather data: {finalData}, generate a concise and informative weather report.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error in getWeather: {e}")
            return None
        except Exception as e:
            logging.error(f"Error in getWeather: {e}")
            return None

    @lru_cache(maxsize=32)
    def getNews(self, api_key=newsAPI, num_articles=5):
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        try:
            logging.debug("Fetching news data")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            logging.debug(f"API Response: {data}")

            articles = data.get("articles", [])
            if len(articles) < num_articles:
                logging.warning(f"Only {len(articles)} articles available, cannot select {num_articles}")
                return []

            selected_articles = random.sample(articles, min(num_articles, len(articles)))

            newsSet = set()
            for article in selected_articles:
                news = Gpt.generate_text_response(f"Summarize the given article in a journalistic style, focusing on the key points and events. Please avoid including any hyperlinks.\n{article}")
                self.playChime('success')
                newsSet.add(news)

            return newsSet
        except requests.exceptions.RequestException as e:
            self.playChime('error')
            logging.error(f"Error in getNews: {e}")
            return set()
        except Exception as e:
            self.playChime('error')
            logging.error(f"Error in getNews: {e}")
            return set()

    def get_part_of_day(self):
        current_hour = datetime.now().hour
        logging.debug(f"Current hour: {current_hour}")

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
            logging.error(f"Error in startMyDay: {e}")

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
            logging.debug(f"Sending email to {recipient} with subject {subject}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
            logging.info("Email sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email. Error: {e}")