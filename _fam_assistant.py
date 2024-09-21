import pyaudio
import pvporcupine
import threading
import struct
import subprocess
import difflib
import sys
import libs.utilities as Utilities
import libs.gpt as gpt
import libs.music as musicP
import libs.music_search as musicSearch
import libs.clock as clock

commands = {"search task", "search for task", "how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play music", "pause", "resume", "stop", "next", "skip", "add task", "seek forward", "shut down"}

class FamAssistant:
    def __init__(self, access_key, keyword_path, music_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.musicSearch = musicSearch.MusicSearch()
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)
        self.task_manager = clock.TaskManager()
        self.util = Utilities.Utilities()
        self.gpt = gpt.Generation()

    def init_porcupine(self):
        try:
            self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
        except Exception as e:
            print(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None 
            
    def init_audio_stream(self):
        pa = pyaudio.PyAudio()
        if self.porcupine is not None:
            self.audio_stream = pa.open(
                rate=44100,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

    def start(self):
        self.init_porcupine()
        self.init_audio_stream()
        self.is_running = True
        print("Listening for keyword...")
    
        while self.is_running:
            if self.porcupine is not None and self.audio_stream is not None:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
    
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.on_keyword_detected()
                    print("Listening for keyword...")

    def on_keyword_detected(self):
        print("Keyword detected!")
        self.util.speak("Keyword detected. Listening for your command...")
        if self.music_player.is_playing:
            self.music_player.set_volume(20)
        try:
            command = self.util.getSpeech()
        except Exception as e:
            print(f"Error in speech recognition {e}")
            return
        print(f"Recognized command: {command}")
        if self.music_player.is_playing and command != "stop music" and not any(keyword in command for keyword in ["song", "music"]):
            self.util.speak("Please stop the music player first by saying 'stop music'.")
        else:
            self.process_command(command)
        if self.music_player.is_playing:
            self.music_player.set_volume(100)

    def process_command(self, command):
        print(f"Processing command: {command}")
        command_words = command.lower().split()
        first_few_words = " ".join(command_words[:4])

        if any(cmd in first_few_words for cmd in commands):
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
                reply = str(self.gpt.generate_text_with_image(f"{command}", r"F:\ai-assistant\pico-files\assets\image.jpg"))
                self.util.playChime('load')
                self.util.speak(reply)
            elif any(start in command for start in ["start", "start my day", "good morning"]):
                self.util.startMyDay()
            elif any(news in command for news in ["news", "daily news", "what's happening", "what's the news"]):
                self.util.speak("Here are the top news headlines...")
                news = self.util.getNews()
                for headline in news:
                    self.util.speak(headline)
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
                try:
                    seconds = 10
                    self.util.speak(f"Seeking forward by {seconds} seconds")
                    self.music_player.seek_forward(seconds)
                except ValueError:
                    self.util.speak("Invalid time. Please provide the number of seconds to seek forward.")
            elif "shut down" in command or "shutdown" in command:
                self.util.speak("Quitting the program")
                self.stop()
                sys.exit(0)
            elif "play" in command: 
                song_name = command.replace("play", "").strip()
                if song_name:
                    subprocess.run(["/home/pi/FAM/env/bin/python3", "/home/pi/FAM/libs/music_search.py", song_name])
                    self.util.speak(f"{song_name} will be played shortly...")
                    self.music_player.play_music_thread()
            elif any(task in command for task in ["add task", "add a task", "add a new task"]):
                task = self.util.speak("Please provide the task!")
                if task:
                    self.util.speak(f"Adding task: {task}")
                    self.task_manager.add_task_at_start(task)
            elif any(search in command for search in ["search task", "search for task"]):
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
        else:
            # Fallback to GPT-based response for unrecognized commands
            reply = str(self.gpt.live_chat_with_ai(str(command)))
            self.util.speak(reply)

    def stop(self):
        self.is_running = False
        if self.audio_stream is not None:
            self.audio_stream.close()
        if self.porcupine is not None:
            self.porcupine.delete()
        self.music_player.stop_music()

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()