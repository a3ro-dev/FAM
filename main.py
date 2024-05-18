import pyttsx3
import speech_recognition as sr
engine = pyttsx3.init()
from libs import gpt

Gpt = gpt.Generation()

class Utilities:
    def __init__(self):
        pass

    def speak(self, text: str):
        engine.say(text)
        engine.runAndWait()

    def getSpeech(self):
        pass

    def getTime(self):
        import time
        return time.ctime()

    def getDate(self):
        from datetime import datetime
        # Get the current date
        now = datetime.now()
        # Format the date as "October 1st, 2023"
        speech_friendly_date = now.strftime("%B %d, %Y").replace(" 0", " ")
        # Add suffix for the day
        day = now.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        final_date = f"{speech_friendly_date[:-5]}{suffix}, {speech_friendly_date[-4:]}"
        return final_date
    
    def getWeather(self, city: str):
        import requests
        api_key = "054b217266c57c45c2c6dca381babd9f"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}"
        response = requests.get(url)
        data = response.json()
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
    
        Gpt.generate_text_response(f"Generate a concise weather report with given data.\n{finalData}", max_tokens=100)

    def getNews(self):
        import requests
        api_key = "67971eebe05d4dffaed478cf1560f4cd"
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        articles = data["articles"]
        for article in articles:
            Gpt.generate_text_response(f"Generate a concise news report with given data.\n{article}", max_tokens=100)
    