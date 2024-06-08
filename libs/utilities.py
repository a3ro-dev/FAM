import pyttsx3
import libs.gpt as gpt
import json
import random
import pyaudio
from vosk import Model, KaldiRecognizer
from audioplayer import AudioPlayer
import time
import cv2

Gpt = gpt.Generation()

model_path = r'F:\ai-assistant\pico-files\model\vosk-model-en-in-0.5'
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

class Utilities:
    def __init__(self):
        self.author = "AKSHAT SINGH KUSHWAHA"
        self.audio_files = {
            "success": "F:/ai-assistant/pico-files/assets/audio/success.mp3",
            "error": "F:/ai-assistant/pico-files/assets/audio/error.mp3",
            "load": "F:/ai-assistant/pico-files/assets/audio/load.mp3"
        }

    def playChime(self, type: str):
        if type in self.audio_files:
            AudioPlayer(self.audio_files[type]).play(block=True)
        else:
            print(f"Unknown chime type: {type}")

    def speak(self, text: str):
        engine = pyttsx3.init()
        print(f"Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
        print(text)

    def getSpeech(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
            stream.start_stream()
            print("Listening for speech...")
            start_time = time.time()
            while True:
                data = stream.read(4096, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result)["text"]
                    print(f"Recognized speech: {text}")
                    self.playChime('success')
                    return str(text)
                elif not recognizer.PartialResult():
                    print("User stopped speaking.")
                    break
                if time.time() - start_time > 10:  # Listen for 10 seconds
                    print("Listening timeout.")
                    break
        except Exception as e:
            self.playChime('error')
            print(f"Error in getSpeech: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def getTime(self):
        import time
        return time.ctime()

    def getDate(self):
        from datetime import datetime
        now = datetime.now()
        speech_friendly_date = now.strftime("%B %d, %Y").replace(" 0", " ")
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
        weather = Gpt.generate_text_response(f"Generate a concise weather report with given data.\n{finalData}")
        # weather = 'it is good weather today.'
        return weather


    def getNews(self):
        import requests
        api_key = "67971eebe05d4dffaed478cf1560f4cd"
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        articles = data["articles"]
        newsList = []

        # Randomly select 5 articles
        selected_articles = random.sample(articles, 5)

        for article in selected_articles:
            news = Gpt.generate_text_response(f"Generate a concise news report with given data.\n{article}")
            self.playChime('success')
            newsList.append(news)

        return newsList

    def startMyDay(self):
        location = 'Allahabad'
        self.speak("Good Morning!")
        self.speak(f"Today is {self.getDate()}")
        self.speak(f"The current time is {self.getTime()}")
        weather_report = str(self.getWeather(location))
        self.speak(weather_report)
        news_headlines = self.getNews()
        self.speak("Here are today's top news headlines.")
        for news in news_headlines:
            self.speak(news)
        self.speak("That's all for now. Have a great day!")

    def send_email(self, recipient: str, subject: str, content: str):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import smtplib

        sender_email = "your_email@gmail.com"
        sender_password = "your_password"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject

        body = f"{content}\n\nSent from your assistant."
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()

    def captureImage(self):
        # Delay for 2 seconds
        time.sleep(1)
        
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            self.playChime('error')
            raise Exception("Failed to open camera")
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        ret, frame = camera.read()
        if not ret:
            self.playChime('error')
            raise Exception("Failed to capture image")

        cv2.imwrite(r"F:\ai-assistant\pico-files\assets\image.jpg", frame)
        self.playChime('success')
        camera.release()  
