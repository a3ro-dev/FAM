from datetime import datetime, timedelta
import pyaudio
import pvporcupine
import threading
import struct
import difflib
import sys
import libs.utilities as Utilities
import libs.gpt as gpt
import libs.music as musicP
import libs.music_search as musicSearch
import libs.clock as clock
import libs.bluetooth_manager as btm
import subprocess
import socket
import libs.games
import numpy as np
import logging
import RPi.GPIO as GPIO
import concurrent.futures
import time
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import wordnet
# from nltk.stem import WordNetLemmatizer
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ip_address():
    """Get the IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Attempt to connect to a non-existent IP to determine local IP.
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        logging.error("Failed to get IP address. Using 127.0.0.1 as default.")
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address


# class CommandProcessor:
#     def __init__(self):
#         self.lemmatizer = WordNetLemmatizer()

#     def get_wordnet_pos(self, word):
#         """Map POS tag to first character lemmatize() accepts."""
#         tag = nltk.pos_tag([word])[0][1][0].upper()
#         tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
#         return tag_dict.get(tag, wordnet.NOUN)

#     def preprocess_command(self, command):
#         """Preprocess the command text: tokenize, lemmatize, and return cleaned words."""
#         tokens = word_tokenize(command.lower())  # Tokenize and lowercase the input
#         lemmatized_tokens = [self.lemmatizer.lemmatize(token, self.get_wordnet_pos(token)) for token in tokens]
#         return lemmatized_tokens

#     def extract_time(self, tokens):
#         """Extract time information from tokens."""
#         time_units = {"minute": "minutes", "hour": "hours", "second": "seconds"}
#         number_words = {
#             "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
#             "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
#             "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
#             "sixty": 60,
#         }
#         time_value = 0
#         time_unit = "seconds"
#         time_str = ""
#         am_pm = ""
#         i = 0
#         while i < len(tokens):
#             token = tokens[i]
#             if token.isdigit():
#                 time_str += token
#             elif token in number_words:
#                 time_str += str(number_words[token])
#             elif token == "half":
#                 time_str += ".5"
#             elif token in ["am", "pm"]:
#                 am_pm = token
#             elif token in time_units.values():
#                 time_unit = token
#                 break
#             i += 1

#         # Convert time_str to a datetime object if it's in the format of HHMM or HMM
#         if len(time_str) in [3, 4]:
#             try:
#                 time_format = "%I%M %p" if am_pm else "%H%M"
#                 time_value = datetime.strptime(time_str + " " + am_pm, time_format).time()
#             except ValueError:
#                 pass

#         return time_value, time_unit

#     def command_matches(self, command_tokens, command_set):
#         """Check if command tokens match any of the known commands using synonym matching."""
#         for token in command_tokens:
#             for known_command in command_set:
#                 if token in known_command:
#                     return True
#         return False

#     def process_command(self, command, commands):
#         """Process the input command."""
#         command_tokens = self.preprocess_command(command)
        
#         # Matching command tokens with known commands
#         if self.command_matches(command_tokens, commands):
#             return "Known command detected!"
#         else:
#             return "Unknown command. Let me try searching online!"
        
class GestureModule:
    def __init__(self, trigger_pin=18, echo_pin=24, distance_range=(2, 5), gesture_interval=0.2, debounce_time=1.0):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.distance_range = distance_range
        self.gesture_interval = gesture_interval
        self.debounce_time = debounce_time
        self.distance_history = deque(maxlen=3)  # Shorter moving average window
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, False)  # Ensure trigger pin is off

    def cleanup_gpio(self):
        GPIO.cleanup()

    def measure_distance(self):
        try:
            # Trigger the sensor
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, False)

            start_time = time.time()
            stop_time = time.time()

            # Capture pulse start
            while GPIO.input(self.echo_pin) == 0:
                start_time = time.time()
                if time.time() - start_time > 0.02:  # Timeout if sensor takes too long
                    return None

            # Capture pulse end
            while GPIO.input(self.echo_pin) == 1:
                stop_time = time.time()
                if stop_time - start_time > 0.02:  # Timeout if sensor takes too long
                    return None

            # Calculate distance (Time * Speed of Sound / 2)
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2  # Distance in cm

            return distance
        except Exception as e:
            logging.warning(f"Error measuring distance: {e}")
            return None

    def get_smoothed_distance(self):
        distance = self.measure_distance()
        if distance is not None:
            self.distance_history.append(distance)
            return np.mean(self.distance_history)  # Moving average smoothing
        return None

    def detect_hand_gesture(self):
        logging.info("Starting hand gesture detection...")
        last_gesture_time = time.time()

        while True:
            current_distance = self.get_smoothed_distance()

            if current_distance is None:
                time.sleep(self.gesture_interval)
                continue

            current_time = time.time()
            if current_time - last_gesture_time < self.debounce_time:
                time.sleep(self.gesture_interval)
                continue

            if self.distance_range[0] <= current_distance <= self.distance_range[1]:
                logging.info("Hand Gesture Detected")
                last_gesture_time = current_time
                return True

            time.sleep(self.gesture_interval)

    def start_hand_gesture_detection(self):
        hand_gesture_thread = threading.Thread(target=self.detect_hand_gesture, daemon=True)
        hand_gesture_thread.start()

    def stop(self):
        logging.info("Stopping gesture detection...")
        self.cleanup_gpio()

class FamAssistant:
    def __init__(self, access_key, keyword_path, music_path):
        """Initialize the assistant with keyword detection, music player, utilities, etc."""
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.music_path = music_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.thread = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.games = libs.games.Games(False, '/home/pi/FAM/misc')    
        self.musicSearch = musicSearch.MusicSearch()
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)
        self.task_manager = clock.TaskManager()
        self.util = Utilities.Utilities()
        self.gpt = gpt.Generation()
        self.gesture_module = GestureModule()
        self.bt_manager = btm.BluetoothManager()
        # self.command_processor = CommandProcessor()

        logging.info("FamAssistant initialized.")

    def init_porcupine(self):
        """Initialize the Porcupine wake word detection engine."""
        try:
            self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
            logging.info("Porcupine initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None

    def init_audio_stream(self):
        """Initialize the audio stream for capturing microphone input."""
        try:
            pa = pyaudio.PyAudio()
            if self.porcupine:
                self.audio_stream = pa.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
                logging.info("Audio stream initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize audio stream: {e}")

    def start(self):
        """Start the assistant, initialize resources and begin listening for wake words."""
        try:
            self.gesture_module.start_hand_gesture_detection()
            self.init_porcupine()
            self.init_audio_stream()
            self.is_running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            logging.info("Assistant started and listening for keyword or looking for gesture.")
            self.util.playChime('success')
        except Exception as e:
            logging.error(f"Error in start: {e}")

    def run(self):
        """Run the main loop to detect keywords and respond."""
        try:
            while self.is_running:
                if self.porcupine and self.audio_stream:
                    pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    keyword_index = self.porcupine.process(pcm)
                    if keyword_index >= 0:
                        logging.info("Keyword detected.")
                        self.executor.submit(self.on_keyword_detected)
                if self.gesture_module.detect_hand_gesture():
                    logging.info("Hand gesture detected.")
                    self.executor.submit(self.on_keyword_detected)
        except Exception as e:
            logging.error(f"Error in run loop: {e}")

    def on_keyword_detected(self):
        """Handle the event when a keyword is detected."""
        self.util.playChime('success')
        logging.info("Chime played for keyword detection.")
    
        if self.music_player.is_playing:
            self.music_player.set_volume(20)
    
        self.close_audio_stream()
    
        try:
            command = self.util.getSpeech()
            if not command:  # Check for empty command
                return
            logging.debug(f"Recognized command: {command}")
        except Exception as e:
            logging.error(f"Error in speech recognition: {e}")
            self.init_audio_stream()  # Ensure audio stream is reinitialized
            return
    
        if self.music_player.is_playing and "stop" not in command.lower() and not {"song", "music"} & set(command.lower().split()): # type: ignore
            logging.error("Please stop the music player first by saying 'stop music'.")
        else:
            self.process_command(command)
    
        if self.music_player.is_playing:
            self.music_player.set_volume(100)
    
        self.init_audio_stream()

    def process_command(self, command):
        """Process the command after detecting the wake word."""
        logging.debug(f"Processing command: {command}")
        command_words = set(command.lower().split())
        if command_words & commands:
            self.handle_known_commands(command.lower())
        else:
            self.handle_unknown_command(command)

    def handle_known_commands(self, command):
        # processed_tokens = self.command_processor.preprocess_command(command)
        if any(greet in command for greet in ["hi", "hello", "wassup", "what's up", "hey", "sup"]):
            self.repSpeak('/home/pi/FAM/tts_audio_files/Hello__How_can_I_help_you_today_.mp3')
        elif "how are you" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/I_m_doing_great__How_can_I_help_you_today_.mp3')
        elif any(time in command for time in ["time", "what time is it", "current time"]):
            self.util.speak(self.util.getTime())
        elif any(date in command for date in ["date", "what's the date", "current date"]):
            self.util.speak(self.util.getDate())
        elif any(start in command for start in ["start", "start my day", "good morning"]):
            self.util.startMyDay()
        elif any(news in command for news in ["news", "daily news", "what's happening", "what's the news"]):
            self.repSpeak('/home/pi/FAM/tts_audio_files/Here_are_the_top_news_headlines___.mp3')
            news = self.util.getNews()
            for headline in news:
                self.util.speak(headline)
        elif "download" in command:
            song_name = command[9:].strip()  # remove download and extract song name
            if song_name:
                subprocess.run(["/home/pi/FAM/env/bin/python3", "/home/pi/FAM/libs/music_search.py", song_name])
                self.util.speak(f"{song_name} downloaded successfully.")
        elif "play music" in command:
            self.music_player.play_music_thread()
        elif "pause" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/Pausing_music___.mp3')
            self.music_player.pause_music()
        elif "resume" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/Unpausing_music___.mp3')
            self.music_player.unpause_music()
        elif "stop" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/Stopping_music___.mp3')
            self.music_player.stop_music()
        elif any(skip in command for skip in ["next", "skip"]):
            self.repSpeak('/home/pi/FAM/tts_audio_files/Playing_next_track___.mp3')
            self.music_player.play_next()
        elif "seek forward" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/Seeking_forward_by_10_seconds.mp3')
            self.seek_forward()
        elif "shut down" in command or "shutdown" in command:
            self.repSpeak('/home/pi/FAM/tts_audio_files/Quitting_the_program.mp3')
            subprocess.run(["sudo", "shutdown", "now"])
            self.stop()
            sys.exit(0)
        elif any(task in command for task in ["add task", "add a task", "add a new task"]):
            self.repSpeak('/home/pi/FAM/tts_audio_files/Please_provide_the_task_.mp3')
            self.add_task()
        elif any(search in command for search in ["search task", "search for task"]):
            self.repSpeak('/home/pi/FAM/tts_audio_files/Please_provide_the_task_to_search_for_.mp3')
            self.search_task()
        elif any(game in command for game in ["play game", "start game"]):
            self.games.play_game()
            ip_address = get_ip_address()
            self.util.send_email(recipient='akshatsingh14372@outlook.com', subject="Fam Games Hub Invite", plain_content='' , html_content=self.returnEmailSubject(ip_address))
        elif any(game in command for game in ["stop game", "end game"]):
            self.games.stop_game()
            self.repSpeak('/home/pi/FAM/tts_audio_files/game_over.mp3')
        elif any(bt in command for bt in ["start bluetooth mode", "enable bluetooth mode", "bluetooth speaker mode"]):
            self.bt_manager.start_bluetooth_mode()
            self.util.speak("Bluetooth mode started. The device is now acting as a Bluetooth speaker.")
        elif any(bt in command for bt in ["stop bluetooth mode", "disable bluetooth mode", "exit bluetooth speaker mode"]):
            self.bt_manager.stop_bluetooth_mode()
            self.util.speak("Bluetooth mode stopped.")
        # elif "reminder" in processed_tokens:
        #     try:
        #         time_value, time_unit = self.command_processor.extract_time(processed_tokens)
        #         if time_unit == "minutes":
        #             reminder_time = datetime.now() + timedelta(minutes=time_value)
        #         elif time_unit == "hours":
        #             reminder_time = datetime.now() + timedelta(hours=time_value)
        #         elif time_unit == "seconds":
        #             reminder_time = datetime.now() + timedelta(seconds=time_value)
        #         else:
        #             raise ValueError("Unsupported time unit")
                
        #         message = " ".join(processed_tokens[processed_tokens.index("to") + 1:]) if "to" in processed_tokens else ""
        #         self.task_manager.set_reminder(reminder_time.strftime("%Y-%m-%d %H:%M:%S"), message)
        #         self.util.speak(f"Reminder set for {time_value} {time_unit} to {message}")
        #     except Exception as e:
        #         logging.error(f"Error setting reminder: {e}")
        #         self.util.speak("Sorry, I couldn't set the reminder.")
        # elif "timer" in processed_tokens:
        #     try:
        #         time_value, time_unit = self.command_processor.extract_time(processed_tokens)
        #         if time_unit == "minutes":
        #             seconds = time_value * 60
        #         elif time_unit == "hours":
        #             seconds = time_value * 3600
        #         elif time_unit == "seconds":
        #             seconds = time_value
        #         else:
        #             raise ValueError("Unsupported time unit")
                
        #         self.task_manager.set_timer(float(seconds))
        #         self.util.speak(f"Timer set for {time_value} {time_unit}.")
        #     except Exception as e:
        #         logging.error(f"Error setting timer: {e}")
        #         self.util.speak("Sorry, I couldn't set the timer.")
        # elif "stopwatch" in processed_tokens:
        #     if "start" in processed_tokens:
        #         self.task_manager.start_stopwatch()
        #         self.util.speak("Stopwatch started.")
        #     elif "stop" in processed_tokens:
        #         self.task_manager.stop_stopwatch()
        #         self.util.speak("Stopwatch stopped.")
        # elif "alarm" in processed_tokens:
        #     try:
        #         time_str = " ".join(processed_tokens[processed_tokens.index("for") + 1:])
        #         self.task_manager.set_alarm(time_str)
        #         self.util.speak(f"Alarm set for {time_str}")
        #     except Exception as e:
        #         logging.error(f"Error setting alarm: {e}")
        #         self.util.speak("Sorry, I couldn't set the alarm.")
                
    def repSpeak(self, file):
        subprocess.run(['ffplay', '-nodisp', '-autoexit', file], check=True)

    def seek_forward(self):
        try:
            seconds = 10
            self.util.speak(f"Seeking forward by {seconds} seconds")
            self.music_player.seek_forward(seconds)
        except ValueError:
            self.util.speak("Invalid time. Please provide the number of seconds to seek forward.")

    def add_task(self):
        task = self.util.speak("Please provide the task!")
        if task:
            self.util.speak(f"Adding task: {task}")
            self.task_manager.add_task_at_start(task)

    def search_task(self):
        task = self.util.speak("Please provide the task to search for!")
        if task:
            self.util.speak(f"Searching for task: {task}")
            tasks = [task.name for task in self.task_manager.display_tasks()]
            close_matches = difflib.get_close_matches(task, tasks, n=1, cutoff=0.7)
            if close_matches:
                matched_task = close_matches[0]
                self.task_manager.search_task(matched_task)
            else:
                self.util.speak("No matching task found.")

    def handle_unknown_command(self, command):
        """Handle unknown commands by using the AI chat inference."""
        logging.info(f"Handling unknown command: {command}")
        reply = str(self.gpt.live_chat_with_ai(str(command)))
        self.util.speak(reply)

    def close_audio_stream(self):
        """Close the audio stream to free up resources."""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            logging.info("Audio stream closed.")

    def stop(self):
        """Stop the assistant and clean up resources."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        self.close_audio_stream()
        if self.porcupine:
            self.porcupine.delete()
        self.music_player.stop_music()
        logging.info("Assistant stopped.")

    def run_in_thread(self):
        """Run the assistant in a separate thread."""
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def returnEmailSubject(self, ip_address):
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fam Games Hub</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 15px;
                    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    padding: 20px;
                    max-width: 600px;
                    width: 100%;
                    text-align: center;
                }}
                h1 {{
                    color: #333;
                }}
                p {{
                    color: #666;
                    line-height: 1.6;
                }}
                a.button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 20px 0;
                    font-size: 16px;
                    color: #fff;
                    background-color: #007bff;
                    border-radius: 5px;
                    text-decoration: none;
                    transition: background-color 0.3s ease;
                }}
                a.button:hover {{
                    background-color: #0056b3;
                }}
                .faq {{
                    text-align: left;
                    margin-top: 20px;
                }}
                .faq h2 {{
                    color: #333;
                }}
                .faq p {{
                    color: #666;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        padding: 15px;
                    }}
                    a.button {{
                        font-size: 14px;
                        padding: 8px 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Fam Games Hub</h1>
                <p>To launch the Fam Games Hub, simply click the button below:</p>
                <a href="http://{ip_address}:8080" class="button">Launch Fam Games Hub</a>
                <div class="faq">
                    <h2>FAQs</h2>
                    <h3>What is Fam Games Hub?</h3>
                    <p>Fam Games Hub is an integrated feature of <a href="https://fam-ai-web.streamlit.app/" target="_blank">Fam Assistant</a> that allows you to launch and manage games directly from your device. With just a simple command, you can start a game server and enjoy your favorite games.</p>
                    <p>We hope you enjoy this new feature. If you have any questions or need assistance, feel free to reach out to our support team.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        return html_content
    
# Define known commands as a set for faster lookup
commands = {
    "search task", "search for task", "how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", 
    "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", "end",
    "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play", 
    "play music", "pause", "resume", "stop", "next", "skip", "add task", "seek forward", "shut down", "shutdown", "music",
    "start bluetooth mode", "enable bluetooth mode", "bluetooth speaker mode", "stop bluetooth mode", "disable bluetooth mode", "exit bluetooth speaker mode",
    "set reminder", "set timer", "start stopwatch", "stop stopwatch", "set alarm"
}