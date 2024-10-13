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
import subprocess
import socket
import libs.games
import numpy as np
import logging

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
        self.games = libs.games.Games(False, '/home/pi/FAM/misc')    
        self.musicSearch = musicSearch.MusicSearch()
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)
        self.task_manager = clock.TaskManager()
        self.util = Utilities.Utilities()
        self.gpt = gpt.Generation()

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
            self.init_porcupine()
            self.init_audio_stream()
            self.is_running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            logging.info("Assistant started and listening for keyword.")
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
                        self.on_keyword_detected()
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
            self.util.speak("Please stop the music player first by saying 'stop music'.")
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
            self.handle_known_commands(command)
        else:
            self.handle_unknown_command(command)

    def handle_known_commands(self, command):
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
            self.util.speak(f"Game started on http://{ip_address}:8080. Have Fun!") 
        elif any(game in command for game in ["stop game", "end game"]):
            self.games.stop_game()
            self.repSpeak('/home/pi/FAM/tts_audio_files/game_over.mp3')
    
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

# Define known commands as a set for faster lookup
commands = {
    "search task", "search for task", "how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", 
    "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", 
    "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play", 
    "play music", "pause", "resume", "stop", "next", "skip", "add task", "seek forward", "shut down", "shutdown", "music"
}