"""
Utility Module for FAM (File Assistant Manager)

This module provides various utility functions for managing system operations, including:
- Audio playback and text-to-speech
- Speech recognition
- Weather information retrieval
- News fetching
- Email sending
- Time and date management

The module uses configuration from 'conf/config.yaml' for API keys and settings.

Dependencies:
    - openai: For text-to-speech conversion
    - speech_recognition: For speech input
    - pydub: For audio processing
    - yaml: For configuration management
    - requests: For API calls
    - smtplib: For email functionality
"""

import libs.gpt as gpt
import random
import time
import speech_recognition as sr # type: ignore
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
    A utility class providing various system operation functions.

    This class handles common operations like audio playback, speech recognition,
    weather updates, news fetching, and email communications.

    Attributes:
        author (str): The system author name from config
        audio_files (dict): Mapping of audio file types to their paths
            - 'success': Path to success sound
            - 'error': Path to error sound
            - 'load': Path to loading sound
    """

    def __init__(self):
        """Initialize Utilities with author name and audio file paths."""
        self.author = author    
        self.audio_files = {
            "success": success,
            "error": error,
            "load": load
        }
        logging.info("Utilities class initialized.")

    def playChime(self, type: str) -> None:
        """
        Play a chime sound of the specified type.

        Args:
            type (str): Type of chime ('success', 'error', or 'load')

        Raises:
            ValueError: If the chime type is unknown
        """
        try:
            if type in self.audio_files:
                logging.debug(f"Playing chime of type: {type}")
                subprocess.run(['ffplay', '-nodisp', '-autoexit', self.audio_files[type]], check=True)
            else:
                raise ValueError(f"Unknown chime type: {type}")
        except Exception as e:
            logging.error(f"Error in playChime: {e}")

    def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Args:
            text (str): The text to be converted to speech

        Notes:
            Uses OpenAI's TTS model 'tts-1' with 'shimmer' voice
        """
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

    def getSpeech(self) -> str:
        """
        Listen for and recognize speech input.

        Returns:
            str: The recognized text, or empty string if recognition fails

        Notes:
            Requires FLAC codec to be installed on the system
        """
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

    def getTime(self) -> str:
        """
        Get the current system time.

        Returns:
            str: Formatted current time string
        """
        current_time = time.ctime()
        logging.info(f"Current time: {current_time}")
        return current_time
    
    def getDate(self) -> str:
        """
        Get the current date with proper ordinal suffix.

        Returns:
            str: Formatted date string (e.g., "December 25th, 2023")
        """
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
        """
        Fetch weather information for a specified city.

        Args:
            city (str): Name of the city
            api_key (str, optional): OpenWeatherMap API key

        Returns:
            str: Formatted weather report or error message
        """
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
    def getNews(self, api_key=newsAPI, num_articles=3) -> set:
        """
        Fetch and summarize top news articles.

        Args:
            api_key (str, optional): News API key
            num_articles (int, optional): Number of articles to fetch (default: 3)

        Returns:
            set: Set of summarized news articles

        Notes:
            Results are cached using lru_cache
        """
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
                return {0}
    
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

    def get_part_of_day(self) -> str:
        """
        Determine the current part of the day.

        Returns:
            str: One of 'morning', 'afternoon', 'evening', 'night', or 'unknown'
        """
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

    def startMyDay(self, location='Allahabad') -> None:
        """
        Provide a morning briefing with date, weather, and news.

        Args:
            location (str, optional): City for weather info (default: 'Allahabad')

        Notes:
            Combines multiple utility functions to create a comprehensive briefing
        """
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

    def send_email(self, recipient: str, subject: str, plain_content: str, html_content: str = "") -> None:
        """
        Send an email with optional HTML content.

        Args:
            recipient (str): Recipient email address
            subject (str): Email subject
            plain_content (str): Plain text content
            html_content (str, optional): HTML content

        Notes:
            Uses Gmail SMTP server
        """
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
