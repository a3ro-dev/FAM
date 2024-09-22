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

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

class FamAssistant:
    def __init__(self, access_key, keyword_path, music_path):
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

    def init_porcupine(self):
        try:
            self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
            print("Porcupine initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None

    def init_audio_stream(self):
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
                print("Audio stream initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize audio stream: {e}")

    def start(self):
        try:
            self.init_porcupine()
            self.init_audio_stream()
            self.is_running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            print("Listening for keyword...")
        except Exception as e:
            print(f"Error in start: {e}")

    def run(self):
        try:
            while self.is_running:
                if self.porcupine and self.audio_stream:
                    pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    pcm = np.array(pcm, dtype=np.float32)
                    keyword_index = self.porcupine.process(pcm) #type: ignore
                    if keyword_index >= 0:
                        self.on_keyword_detected()
                        print("Listening for keyword...")
        except Exception as e:
            print(f"Error in run: {e}")

    def on_keyword_detected(self):
        print("Keyword detected!")
        self.util.playChime('success')
        if self.music_player.is_playing:
            self.music_player.set_volume(20)

        self.close_audio_stream()

        try:
            command = self.util.getSpeech()
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return

        print(f"Recognized command: {command}")
        if self.music_player.is_playing and command != "stop music" and not any(keyword in command for keyword in ["song", "music"]):
            self.util.speak("Please stop the music player first by saying 'stop music'.")
        else:
            self.process_command(command)

        if self.music_player.is_playing:
            self.music_player.set_volume(100)

        self.init_audio_stream()

    def process_command(self, command):
        print(f"Processing command: {command}")
        command_words = set(command.lower().split())
    
        if command_words & commands:
            self.handle_known_commands(command)
        else:
            self.handle_unknown_command(command)

    def handle_known_commands(self, command):
        if any(greet in command for greet in ["hi", "hello", "wassup", "what's up", "hey", "sup"]):
            self.util.speak("Hello! How can I help you today?")
        elif "how are you" in command:
            self.util.speak("I'm doing great! How can I help you today?")
        elif any(time in command for time in ["time", "what time is it", "current time"]):
            self.util.speak(self.util.getTime())
        elif any(date in command for date in ["date", "what's the date", "current date"]):
            self.util.speak(self.util.getDate())
        elif any(vision in command for vision in ["vision", "eyes", "look", "see", "camera"]):
            self.util.captureImage()
            reply = str(self.gpt.generate_text_with_image(f"{command}", r"assets/image.jpg"))
            self.util.playChime('load')
            self.util.speak(reply)
        elif any(start in command for start in ["start", "start my day", "good morning"]):
            self.util.startMyDay()
        elif any(news in command for news in ["news", "daily news", "what's happening", "what's the news"]):
            self.util.speak("Here are the top news headlines...")
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
            self.util.speak("Pausing music...")
            self.music_player.pause_music()
        elif "resume" in command:
            self.util.speak("Unpausing music...")
            self.music_player.unpause_music()
        elif "stop" in command:
            self.util.speak("Stopping music...")
            self.music_player.stop_music()
        elif any(skip in command for skip in ["next", "skip"]):
            self.util.speak("Playing next track...")
            self.music_player.play_next()
        elif "seek forward" in command:
            self.seek_forward()
        elif "shut down" in command or "shutdown" in command:
            self.util.speak("Quitting the program")
            self.stop()
            sys.exit(0)
        elif any(task in command for task in ["add task", "add a task", "add a new task"]):
            self.add_task()
        elif any(search in command for search in ["search task", "search for task"]):
            self.search_task()
        elif any(game in command for game in ["play game", "start game"]):
            self.games.play_game()
            ip_address = get_ip_address()
            self.util.speak(f"Game started on http://{ip_address}:8080. Have Fun!") 
        elif any(game in command for game in ["stop game", "end game"]):
            self.games.stop_game()
            self.util.speak("Game stopped. Hope you enjoyed!")

    def handle_unknown_command(self, command):
        reply = str(self.gpt.live_chat_with_ai(str(command)))
        self.util.speak(reply)

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

    def close_audio_stream(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            print("Audio stream closed.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        self.close_audio_stream()
        if self.porcupine:
            self.porcupine.delete()
        self.music_player.stop_music()

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

commands = {
    "search task", "search for task", "how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", 
    "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", 
    "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play", 
    "play music", "pause", "resume", "stop", "next", "skip", "add task", "seek forward", "shut down", "music"
}