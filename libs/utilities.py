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
    """
    Utilities class provides various utility functions such as playing chimes, text-to-speech, speech recognition, 
    fetching current time and date, weather information, news headlines, and sending emails.
    Methods:
        __init__():
            Initializes the Utilities class with author and audio files.
        playChime(type: str):
            Plays a chime sound based on the provided type.
        speak(text: str):
            Converts the provided text to speech and plays the audio.
        getSpeech() -> str:
            Listens for speech input from the microphone and returns the recognized text.
        getTime() -> str:
            Returns the current time as a string.
        getDate() -> str:
            Returns the current date in a formatted string.
        getWeather(city: str, api_key: str) -> str:
            Fetches and returns the weather information for the specified city.
        getNews(api_key: str, num_articles: int = 3) -> set:
            Fetches and returns a set of summarized news articles.
        get_part_of_day() -> str:
            Returns the part of the day (morning, afternoon, evening, night) based on the current time.
        startMyDay(location: str = 'Allahabad'):
            Provides a summary of the current date, time, weather, and news headlines to start the day.
        send_email(recipient: str, subject: str, plain_content: str, html_content: str = ""):
            Sends an email with the specified recipient, subject, plain text content, and optional HTML content.
    """
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
        if text.strip():  # Check if the text is not empty or whitespace
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
        else:
            logging.error("Text to be spoken is empty or whitespace.")

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
        try:
            now = datetime.now()
            day = now.day
            
            # Determine the suffix for the day
            if 11 <= day <= 13:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            
            # Format the current date
            current_date = now.strftime(f"%B {day}{suffix}, %Y")
            
            # Log the current date
            logging.info(f"Current date: {current_date}")
            
            return current_date
        except Exception as e:
            logging.error(f"Error in getDate: {e}")
            return ''
    
    def getWeather(self, city: str, api_key=weatherAPI) -> str:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}"
        try:
            logging.debug(f"Fetching weather data for city: {city}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
    
            # Convert temperatures from Kelvin to Celsius
            for key in {"temp", "feels_like", "temp_min", "temp_max"}:
                data["main"][key] -= 273.15
    
            # Extract only the necessary information
            weather_data = {
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temp": round(data["main"]["temp"], 2),
                "feels_like": round(data["main"]["feels_like"], 2),
                "temp_min": round(data["main"]["temp_min"], 2),
                "temp_max": round(data["main"]["temp_max"], 2),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "location": data["name"],
            }
    
            logging.debug(f"Weather data: {weather_data}")
    
            # Generate a concise weather report
            prompt = (
                f"Weather report for {weather_data['location']}: "
                f"Condition: {weather_data['condition']} ({weather_data['description']}). "
                f"Temperature: {weather_data['temp']}°C (feels like {weather_data['feels_like']}°C). "
                f"Min/Max: {weather_data['temp_min']}°C/{weather_data['temp_max']}°C. "
                f"Humidity: {weather_data['humidity']}%. "
                f"Wind speed: {weather_data['wind_speed']} m/s."
            )
    
            return Gpt.generate_text_response(prompt)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error in getWeather: {e}")
            return "Unable to fetch weather data at the moment."
        except Exception as e:
            logging.error(f"Unexpected error in getWeather: {e}")
            return "An error occurred while processing the weather data."
    
    @lru_cache(maxsize=32)
    def getNews(self, api_key=newsAPI, num_articles=3):
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
                # Extract necessary information to minimize token usage
                title = article.get("title", "")
                description = article.get("description", "")
                content = article.get("content", "")
    
                # Create a concise prompt for the GPT model
                prompt = (
                    f"Summarize the following article in a journalistic style, focusing on the key points and events. "
                    f"Title: {title}\n"
                    f"Description: {description}\n"
                    f"Content: {content}\n"
                    "Please avoid including any hyperlinks."
                )
    
                news = Gpt.generate_text_response(prompt)
                self.playChime('success')
                newsSet.add(news)
    
            return newsSet
        except requests.exceptions.RequestException as e:
            self.playChime('error')
            logging.error(f"Error in getNews: {e}")
            return set()
        except Exception as e:
            self.playChime('error')
            logging.error(f"Unexpected error in getNews: {e}")
            return set()

    def get_part_of_day(self):
        try:
            current_hour = datetime.now().hour
            logging.debug(f"Current hour: {current_hour}")
    
            if 0 <= current_hour < 12:
                return "morning"
            elif 12 <= current_hour < 17:
                return "afternoon"
            elif 17 <= current_hour < 20:
                return "evening"
            elif 20 <= current_hour < 24:
                return "night"
            else:
                logging.error(f"Unexpected hour value: {current_hour}")
                return "unknown"
        except Exception as e:
            logging.error(f"Error in get_part_of_day: {e}")
            return "unknown"

    def startMyDay(self, location='Allahabad'):
        try:
            part_of_day = self.get_part_of_day()
            date = self.getDate()
            time = self.getTime()
            
            # Combine greetings, date, and time into a single speech output
            self.speak(f"Good {part_of_day}! Today is {date}.")
            
            # Fetch and speak the weather report
            weather_report = self.getWeather(location)
            if weather_report:
                self.speak(f"{weather_report}")
            else:
                self.speak(f"Sorry, I couldn't fetch the weather for {location}.")
            
            # Fetch and speak the news headlines
            news_headlines = self.getNews()
            if news_headlines:
                self.playChime('success')
                self.speak("Here are the top news headlines:")
                for news in news_headlines:
                    self.speak(news)
            else:
                self.playChime('error')
                self.speak("Sorry, I couldn't fetch the news headlines.")
        except Exception as e:
            logging.error(f"Error in startMyDay: {e}")
            self.speak("An error occurred while starting your day.")

    def send_email(self, recipient: str, subject: str, plain_content: str, html_content: str = ""):
        sender_email = emailID
        sender_password = emailPasswd
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject

        # Create the plain-text and HTML parts
        plain_part = MIMEText(plain_content, "plain")
        message.attach(plain_part)

        if html_content:
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

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