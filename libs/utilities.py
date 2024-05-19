import pyttsx3
import speech_recognition as sr
from libs import gpt
Gpt = gpt.Generation()

class Utilities:
    def __init__(self):
        pass

    def speak(self, text: str):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def getSpeech(self):
        speech = input("Enter your speech: ")
        return speech

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
    
        weather = Gpt.generate_text_response(f"Generate a concise weather report with given data.\n{finalData}", max_tokens=100)
        return weather

    def getNews(self):
        import requests
        api_key = "67971eebe05d4dffaed478cf1560f4cd"
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        articles = data["articles"]
        newsList = []
        for article in articles:
            news = Gpt.generate_text_response(f"Generate a concise news report with given data.\n{article}", max_tokens=100)
            newsList.append(news)
        return newsList

    def startMyDay(self):
        location = ''
        self.speak("Good Morning!")
        self.speak(f"Today is {self.getDate()}")
        self.speak(f"The current time is {self.getTime()}")
        self.speak("Here are the top news headlines for today")
        newsList = self.getNews()
        for news in newsList:
            self.speak(news)
        self.speak(self.getWeather(city=location))
        self.speak("That's all for today. Have a great day ahead!")

    def sendMail(self, subject: str, recipient: str, content: str):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import smtplib
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Create a message object
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject

        # Add the email body
        body = f"{content}\n\nSent from your assistant."
        message.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.send_message(message)

        # Disconnect from the SMTP server
        server.quit()
    