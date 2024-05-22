import pyttsx3
import libs.gpt as gpt
Gpt = gpt.Generation()
import json
import pyaudio
from vosk import Model, KaldiRecognizer

model_path = r'F:\ai-assistant\pico-files\model\vosk-model-small-en-in-0.4'
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

class Utilities:
    def __init__(self, porcupine_listener):
        self.porcupine_listener = porcupine_listener

    def speak(self, text: str):
        engine = pyttsx3.init()
        words = text.split()
        for word in words:
            if self.porcupine_listener.keyword_event.is_set():
                return
            engine.say(word)
            engine.runAndWait()

    def getSpeech(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
            stream.start_stream()
            print("Listening...")
            while True:
                data = stream.read(4096, exception_on_overflow = False)
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result)["text"]
                    print(text)
                    return text
        except Exception as e:
            print(e)
        finally:
            return text

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
    
        weather: str = Gpt.generate_text_response(f"Generate a concise weather report with given data.\n{finalData}")
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
            news: str = Gpt.generate_text_response(f"Generate a concise news report with given data.\n{article}")
            newsList.append(news)
        return newsList

    async def startMyDay(self):
        location = 'Allahabad'
        self.speak("Good Morning!")
        if self.porcupine_listener.keyword_event.is_set():
            return
        self.speak(f"Today is {self.getDate()}")
        if self.porcupine_listener.keyword_event.is_set():
            return
        self.speak(f"The current time is {self.getTime()}")
        if self.porcupine_listener.keyword_event.is_set():
            return
        self.speak("Here are the top news headlines for today")
        newsList = self.getNews()
        for news in newsList:
            self.speak(news)
            if self.porcupine_listener.keyword_event.is_set():
                    return
        if location is not None:
            self.speak(self.getWeather(city=location))
            if self.porcupine_listener.keyword_event.is_set():
                return
        else:
            self.speak("Could not retrieve location.")
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
    
    def captureImage(self):
        import cv2
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise Exception("Failed to open camera")

        # Set the camera resolution to the highest possible
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Capture a frame from the camera
        ret, frame = camera.read()
        if not ret:
            raise Exception("Failed to capture image")

        # Save the captured frame as image.jpg in the assets folder
        cv2.imwrite(r"F:\ai-assistant\pico-files\assets\image.jpg", frame)

        # Release the camera
        camera.release()