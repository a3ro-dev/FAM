import pyaudio
import pvporcupine 
import threading
import struct
import sys
import subprocess
import socket
import numpy as np 
import logging
import RPi.GPIO as GPIO
import concurrent.futures
import time
from collections import deque
import difflib

# Import custom modules
import libs.utilities as Utilities
import libs.gpt as gpt
import libs.music as musicP
import libs.music_search as musicSearch
import libs.clock as clock
import libs.raspotify_wrapper as btm
import libs.games
import libs.raspotify_wrapper as rspw  # Update the import

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ip_address():
    """
    Get the IP address of the machine.
    
    Returns:
        str: Local IP address of the machine, or '127.0.0.1' if unable to determine
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))  # Dummy IP
        ip_address = s.getsockname()[0]
    except Exception as e:
        logging.error(f"Failed to get IP address: {e}")
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

class GestureModule:
    """
    Class to handle gesture detection using ultrasonic sensors.
    
    Attributes:
        trigger_pin (int): GPIO pin for trigger signal
        echo_pin (int): GPIO pin for echo signal
        distance_range (tuple): Min and max distance (cm) for gesture detection
        gesture_interval (float): Time between gesture checks in seconds
        debounce_time (float): Minimum time between valid gestures
        distance_history (deque): Recent distance measurements for smoothing
    """
    def __init__(self, trigger_pin=18, echo_pin=24, distance_range=(2, 5), gesture_interval=0.2, debounce_time=1.0):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.distance_range = distance_range
        self.gesture_interval = gesture_interval
        self.debounce_time = debounce_time
        self.distance_history = deque(maxlen=3)
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, False)

    def cleanup_gpio(self):
        GPIO.cleanup()

    def measure_distance(self):
        """
        Measure distance using ultrasonic sensor.
        
        Returns:
            float: Distance in centimeters, or None if measurement fails
        """
        try:
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, False)

            start_time = time.time()
            stop_time = start_time  # Initialize stop_time with default value
            timeout = start_time + 0.02  # 20ms timeout

            # Wait for echo to start
            while GPIO.input(self.echo_pin) == 0 and time.time() < timeout:
                start_time = time.time()

            # Wait for echo to end
            while GPIO.input(self.echo_pin) == 1 and time.time() < timeout:
                stop_time = time.time()

            if time.time() >= timeout:
                logging.debug("Distance measurement timed out")
                return None

            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2  # Speed of sound = 343 m/s

            return distance
        except Exception as e:
            logging.warning(f"Error measuring distance: {e}")
            return None

    def get_smoothed_distance(self):
        """
        Get smoothed distance measurement using rolling average.
        
        Returns:
            float: Smoothed distance in centimeters, or None if measurement fails
        """
        distance = self.measure_distance()
        if distance is not None:
            self.distance_history.append(distance)
            return np.mean(self.distance_history)
        return None

    def detect_hand_gesture(self):
        logging.debug("Starting hand gesture detection...")
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
                logging.info("Hand gesture detected.")
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
    """
    Main class for the FamAssistant, handling voice and gesture interactions.
    
    Attributes:
        access_key (str): API access key for voice services
        keyword_path (str): Path to wake word model file
        music_path (str): Path to music directory
        is_running (bool): Flag indicating if assistant is active
        is_processing_command (bool): Flag indicating command processing state
        executor: ThreadPoolExecutor for concurrent operations
        command_mappings (list): List of (command_phrase, handler_function) tuples
    """
    def __init__(self, access_key, keyword_path, music_path):
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.music_path = music_path
        self.is_running = False
        self.is_processing_command = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.games = libs.games.Games(False, '/home/pi/FAM/misc')
        self.music_search = musicSearch.MusicSearch()
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)
        self.task_manager = clock.TaskManager()
        self.util = Utilities.Utilities()
        self.gpt = gpt.Generation()
        self.gesture_module = GestureModule()
        self.raspotify_wrapper = rspw.RaspotifyWrapper()

        logging.info("FamAssistant initialized.")

        # Command mappings
        self.command_mappings = [
            ("start my day", self.handle_start_my_day),
            ("good morning", self.handle_start_my_day),
            ("what time is it", self.handle_time),
            ("current time", self.handle_time),
            ("what's the date", self.handle_date),
            ("current date", self.handle_date),
            ("add a new task", self.handle_add_task),
            ("add a task", self.handle_add_task),
            ("search for task", self.handle_search_task),
            ("play music", self.handle_play_music),
            ("pause music", self.handle_pause_music),
            ("resume music", self.handle_resume_music),
            ("stop music", self.handle_stop_music),
            ("play game", self.handle_play_game),
            ("start game", self.handle_play_game),
            ("stop game", self.handle_stop_game),
            ("end game", self.handle_stop_game),
            ("download", self.handle_download),
            ("how are you", self.handle_how_are_you),
            ("time", self.handle_time),
            ("date", self.handle_date),
            ("start", self.handle_start_my_day),
            ("news", self.handle_news),
            ("next", self.handle_next_track),
            ("skip", self.handle_next_track),
            ("pause", self.handle_pause_music),
            ("resume", self.handle_resume_music),
            ("stop", self.handle_stop_music),
            ("shutdown", self.handle_shutdown),
            ("enable raspotify", self.handle_enable_raspotify),
            ("start raspotify", self.handle_enable_raspotify),
            ("enable spotify", self.handle_enable_raspotify),
            ("enable discovery", self.handle_enable_raspotify),
            ("disable raspotify", self.handle_disable_raspotify),
            ("stop raspotify", self.handle_disable_raspotify),
            ("disable spotify", self.handle_disable_raspotify),
            ("disable discovery", self.handle_disable_raspotify),
        ]
        # Sort command mappings by phrase length (longest first)
        self.command_mappings.sort(key=lambda x: len(x[0]), reverse=True)

    def start(self):
        """Start the assistant by initializing gesture detection thread."""
        self.is_running = True
        self.util.playChime('success')
        logging.info("Assistant started.")

        # Start gesture detection thread
        gesture_thread = threading.Thread(target=self.gesture_detection_loop, daemon=True)
        gesture_thread.start()

        # Commented out wake word detection thread
        # wake_word_thread = threading.Thread(target=self.wake_word_detection_loop, daemon=True)
        # wake_word_thread.start()

    def gesture_detection_loop(self):
        """Continuously detects hand gestures and triggers command processing."""
        try:
            while self.is_running:
                if not self.is_processing_command and self.gesture_module.detect_hand_gesture():
                    logging.info("Hand gesture detected.")
                    self.executor.submit(self.on_keyword_detected)
        except Exception as e:
            logging.error(f"Error in gesture detection loop: {e}")

    def on_keyword_detected(self):
        self.is_processing_command = True
        self.util.playChime('success')
        logging.info("Chime played for keyword detection.")

        if self.music_player.is_playing:
            self.music_player.set_volume(20)

        # Removed audio stream closing
        # self.close_audio_stream()

        try:
            command = self.util.getSpeech()
            if not command:
                self.is_processing_command = False
                return
            if isinstance(command, list):
                command = ' '.join(map(str, command))
            logging.debug(f"Recognized command: {command}")
        except Exception as e:
            logging.error(f"Error in speech recognition: {e}")
            self.is_processing_command = False
            return

        if self.music_player.is_playing and "stop" not in command.lower() and not {"song", "music"} & set(command.lower().split()):
            logging.error("Please stop the music player first by saying 'stop music'.")
        else:
            self.process_command(command)

        if self.music_player.is_playing:
            self.music_player.set_volume(100)

        # Removed audio stream initialization
        # self.init_audio_stream()
        self.is_processing_command = False
        time.sleep(1)  # Delay before re-enabling gesture detection

    def process_command(self, command):
        """
        Process the input command and invoke the corresponding handler.
        
        Args:
            command (str): Voice command to process
            
        Note:
            Uses fuzzy matching to handle similar commands and confirm with user
        """
        command = command.lower().strip()
        for phrase, handler in self.command_mappings:
            if phrase in command:
                handler(command)
                return

        # Fuzzy matching with known commands
        phrases = [phrase for phrase, _ in self.command_mappings]
        close_matches = difflib.get_close_matches(command, phrases, n=1, cutoff=0.7)
        if close_matches:
            matched_phrase = close_matches[0]
            self.util.speak(f"Did you mean {matched_phrase}?")
            confirmation = self.util.getSpeech()
            if confirmation and 'yes' in confirmation.lower():
                for phrase, handler in self.command_mappings:
                    if phrase == matched_phrase:
                        handler(command)
                        return
        self.handle_unknown_command(command)

    def handle_play_music(self, _command):
        """
        Handle music playback commands.
        
        Allows playing specific songs or playlists, with automatic download
        if requested song is not found locally.
        """
        self.repSpeak('/home/pi/FAM/tts_audio_files/Play_specific_song_or_playlist.mp3')
        response = self.util.getSpeech()
        if response:
            response = response.lower()
            if 'playlist' in response:
                self.music_player.play_music_thread()
            else:
                song_name = response
                if not self.music_player.play_specific_song(song_name):
                    self.util.speak(f"Song '{song_name}' not found locally, attempting to download.")
                    self.handle_download(f"download {song_name}")
                    self.music_player.play_specific_song(song_name)
        else:
            self.music_player.play_music_thread()

    # Handler methods
    def handle_greeting(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Hello__How_can_I_help_you_today_.mp3')

    def handle_how_are_you(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/I_m_doing_great__How_can_I_help_you_today_.mp3')

    def handle_time(self, _command):
        self.util.speak(self.util.getTime())

    def handle_date(self, _command):
        self.util.speak(self.util.getDate())

    def handle_start_my_day(self, _command):
        self.util.startMyDay()

    def handle_news(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Here_are_the_top_news_headlines___.mp3')
        news = self.util.getNews()
        for headline in news:
            self.util.speak(headline)

    def handle_download(self, command):
        song_name = command.replace("download", "").strip()
        if song_name:
            subprocess.run(
                ["/home/pi/FAM/env/bin/python3", "/home/pi/FAM/libs/music_search.py", song_name]
            )
            self.util.speak(f"{song_name} downloaded successfully.")

    def handle_pause_music(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Pausing_music___.mp3')
        self.music_player.pause_music()

    def handle_resume_music(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Unpausing_music___.mp3')
        self.music_player.unpause_music()

    def handle_stop_music(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Stopping_music___.mp3')
        self.music_player.stop_music()

    def handle_next_track(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Playing_next_track___.mp3')
        self.music_player.play_next()

    def handle_shutdown(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Quitting_the_program.mp3')
        subprocess.run(["sudo", "shutdown", "now"])
        self.stop()
        sys.exit(0)

    def handle_add_task(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Please_provide_the_task_.mp3')
        self.add_task()

    def handle_search_task(self, _command):
        self.repSpeak('/home/pi/FAM/tts_audio_files/Please_provide_the_task_to_search_for_.mp3')
        self.search_task()

    def handle_play_game(self, _command):
        self.games.play_game()
        ip_address = get_ip_address()
        self.util.send_email(
            recipient='akshatsingh14372@outlook.com',
            subject="Fam Games Hub Invite",
            plain_content='',
            html_content=self.returnEmailSubject(ip_address)
        )

    def handle_stop_game(self, _command):
        self.games.stop_game()
        self.repSpeak('/home/pi/FAM/tts_audio_files/game_over.mp3')

    def handle_enable_raspotify(self, _command):
        self.raspotify_wrapper.enable_raspotify()
        self.repSpeak('/home/pi/FAM/tts_audio_files/Raspotify_enabled._The_device_is_now_acting_as_a_Spotify_Connect_device..mp3')

    def handle_disable_raspotify(self, _command):
        self.raspotify_wrapper.disable_raspotify()
        self.repSpeak('/home/pi/FAM/tts_audio_files/Raspotify_disabled.mp3')

    def handle_unknown_command(self, command):
        logging.info(f"Handling unknown command: {command}")
        reply = self.gpt.live_chat_with_ai(command)
        if reply:
            self.util.speak(reply)
        else:
            logging.error("No reply from GPT")

    def repSpeak(self, file):
        subprocess.run(['ffplay', '-nodisp', '-autoexit', file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def seek_forward(self):
        seconds = 10
        self.music_player.seek_forward(seconds)

    def add_task(self):
        task = self.util.getSpeech()
        if task:
            if isinstance(task, list):
                task = ' '.join(map(str, task))
            self.util.speak(f"Adding task: {task}")
            self.task_manager.add_task_at_start(task)

    def search_task(self):
        task = self.util.getSpeech()
        if task:
            if isinstance(task, list):
                task = ' '.join(map(str, task))
            self.util.speak(f"Searching for task: {task}")
            tasks = [t.name for t in self.task_manager.display_tasks()]
            close_matches = difflib.get_close_matches(task, tasks, n=1, cutoff=0.7)
            if close_matches:
                matched_task = close_matches[0]
                self.task_manager.search_task(matched_task)
            else:
                self.util.speak("No matching task found.")

    def stop(self):
        """Stops the assistant and cleans up resources."""
        self.is_running = False
        # Removed audio stream closure
        # self.close_audio_stream()
        # if self.porcupine:
        #     self.porcupine.delete()
        self.music_player.stop_music()
        self.gesture_module.stop()
        logging.info("Assistant stopped.")

    def returnEmailSubject(self, ip_address):
        """
        Generate HTML email content for game hub invitation.
        
        Args:
            ip_address (str): Local IP address for game hub URL
            
        Returns:
            str: HTML formatted email content
        """
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
