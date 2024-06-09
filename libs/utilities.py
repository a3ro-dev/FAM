import libs.gpt as gpt
import random
from vosk import Model, KaldiRecognizer
from audioplayer import AudioPlayer
import time
import cv2
from gtts import gTTS
import speech_recognition as sr

Gpt = gpt.Generation()

# model_path = r'F:\ai-assistant\pico-files\model\vosk-model-small-en-in-0.4'
# model = Model(model_path)
# recognizer = KaldiRecognizer(model, 16000)

class Utilities:
    def __init__(self):
        self.author = "AKSHAT SINGH KUSHWAHA"
        self.audio_files = {
            "success": "F:/ai-assistant/pico-files/assets/audio/success.mp3",
            "error": "F:/ai-assistant/pico-files/assets/audio/error.mp3",
            "load": "F:/ai-assistant/pico-files/assets/audio/load.mp3"
        }

    def playChime(self, type: str):
        try:
            if type in self.audio_files:
                AudioPlayer(self.audio_files[type]).play(block=True)
            else:
                raise ValueError(f"Unknown chime type: {type}")
        except Exception as e:
            print(f"Error in playChime: {e}")

    def speak(self, text: str):
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(r"F:\ai-assistant\pico-files\assets\cache\tts.mp3")
        AudioPlayer(r"F:\ai-assistant\pico-files\assets\cache\tts.mp3").play(block=True)
        print(text)

    # def getSpeech(self):
    #    import pyaudio
    #     try:
    #         p = pyaudio.PyAudio()
    #         stream = p.open(format=pyaudio.paInt16, channels=1, rate=20000, input=True, frames_per_buffer=8192)
    #         stream.start_stream()
    #         print("Listening for speech...")
    #         start_time = time.time()
    #         while True:
    #             data = stream.read(4096, exception_on_overflow=False)
    #             if recognizer.AcceptWaveform(data):
    #                 result = recognizer.Result()
    #                 text = json.loads(result)["text"]
    #                 print(f"Recognized speech: {text}")
    #                 self.playChime('success')
    #                 return str(text)
    #             elif not recognizer.PartialResult():
    #                 print("User stopped speaking.")
    #                 break
    #             if time.time() - start_time > 10:  # Listen for 10 seconds
    #                 print("Listening timeout.")
    #                 break
    #     except Exception as e:
    #         self.playChime('error')
    #         print(f"Error in getSpeech: {e}")
    #     finally:
    #         stream.stop_stream()
    #         stream.close()
    #         p.terminate()

    def getSpeech(self):
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening for speech...")
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=1)
                # Adjust the timeout and phrase_time_limit as needed
                audio = r.listen(source, timeout=2)
            
            text = r.recognize(audio)
            print(f"Recognized speech: {text}")
            self.playChime('success')
            return str(text)
        except Exception as e:
            self.playChime('error')
            return f"Error in getSpeech: {e}"
        
    def getTime(self):
        import time
        return time.ctime()

    def getDate(self):
        from datetime import datetime
        now = datetime.now()
        day = now.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        speech_friendly_date = now.strftime(f"%B {day}{suffix}, %Y")
        return speech_friendly_date

    def getWeather(self, city: str, api_key="054b217266c57c45c2c6dca381babd9f"):
        import requests
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Convert temperature from Kelvin to Celsius
            for key in ["temp", "feels_like", "temp_min", "temp_max"]:
                data["main"][key] = data["main"][key] - 273.15

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
            weather = Gpt.generate_text_response(f"Given the following weather data: {finalData}, generate a concise and informative weather report.")
            return weather
        except requests.exceptions.RequestException as e:
            print(f"Error in getWeather: {e}")
            return None
        except Exception as e:
            print(f"Error in getWeather: {e}")
            return None

    def getNews(self, api_key="67971eebe05d4dffaed478cf1560f4cd", num_articles=5):
        import requests
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if len(articles) < num_articles:
                raise Exception(f"Only {len(articles)} articles available, cannot select {num_articles}")
            
            # Randomly select num_articles articles
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
        import datetime
        current_hour = datetime.datetime.now().hour
    
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
    
            self.speak("That's all for now. Have a great {part_of_day}!")
        except Exception as e:
            self.speak(f"Sorry, I encountered an error: {e}")

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

    def captureImage(self, save_path="F:\\ai-assistant\\pico-files\\assets\\image.jpg"):
        try:
            # Delay for 1 second
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
    
            cv2.imwrite(save_path, frame)
            self.playChime('success')
        except Exception as e:
            self.playChime('error')
            print(f"Error in captureImage: {e}")
        finally:
            camera.release()  
            cv2.destroyAllWindows()