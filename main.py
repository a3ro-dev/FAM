import pyaudio
import os
import pvporcupine
import threading
import libs.gpt as gpt
import libs.music as musicP
import libs.music_search as musicSearch
import libs.utilities as utilities
import sys
import platform
import difflib
import yaml
import subprocess
import libs.clock as clock


Gpt = gpt.Generation()
Util = utilities.Utilities()

with open(r'pico-files\conf\config.yaml', 'r') as file:
    config = yaml.safe_load(file)

access_key = config['main']['access_key']
music_path = config['main']['music_path']

commands = {"search task", "search for task", "how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play music", "pause", "resume", "stop", "next", "skip", "add task", "seek forward", "shut down"}

class PorcupineListener:
    def __init__(self, access_key, keyword_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.musicSearch = musicSearch.MusicSearch()
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)
        self.task_manager = clock.TaskManager()

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
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

    def start(self):
        # self.init_porcupine()
        # self.init_audio_stream()
        # self.is_running = True
        # print("Listening for keyword...")
    
        # while self.is_running:
        #     if self.porcupine is not None and self.audio_stream is not None:
        #         pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
        #         pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
    
        #         keyword_index = self.porcupine.process(pcm)
        #         if keyword_index >= 0:
        #             self.on_keyword_detected()
        #             print("Listening for keyword...")
        wake = str(input("Enter 'hey fam' to begin listening for the keyword: "))
        if wake == "hey fam":
            self.on_keyword_detected()
            print("Listening for keyword...")

    def on_keyword_detected(self):
        print("Keyword detected!")
        Util.speak("Keyword detected. Listening for your command...")
        if self.music_player.is_playing:
            self.music_player.set_volume(20)
        try:
            command = Util.getSpeech()
        except Exception as e:
            print(f"Error in speech recognition {e}")
            return
        print(f"Recognized command: {command}")
        if self.music_player.is_playing and command != "stop music" and not any(keyword in command for keyword in ["song", "music"]):
            Util.speak("Please stop the music player first by saying 'stop music'.")
        else:
            self.process_command(command)
        if self.music_player.is_playing:
            self.music_player.set_volume(100)

    def process_command(self, command):
        print(f"Processing command: {command}")
        if any(greet in command for greet in ["how are you", "hi", "hello", "wassup", "what's up", "hey", "sup"]):
            for _ in range(10):
                reply = str(Gpt.live_chat_with_ai(str(command)))
                Util.speak(reply)
                command = Util.getSpeech()
                if command and any(bye in command for bye in ["bye", "goodbye", "stop"]):
                    Util.speak("Goodbye! Have a nice day.")
                    break
        elif any(time in command for time in ["time", "what time is it", "current time"]):
            Util.speak(Util.getTime())
        elif any(date in command for date in ["date", "what's the date", "current date"]):
            Util.speak(Util.getDate())
        elif "vision" in command or "eyes" in command:
            Util.captureImage()
            reply = str(Gpt.generate_text_with_image(f"{command}", r"F:\ai-assistant\pico-files\assets\image.jpg"))
            Util.playChime('load')
            Util.speak(reply)
        elif any(start in command for start in ["start", "start my day", "good morning"]):
            Util.startMyDay()
        elif any(news in command for news in ["news", "daily news", "what's happening", "what's the news"]):
            Util.speak("Here are the top news headlines...")
            news = Util.getNews()
            for headline in news:
                Util.speak(headline)
        elif "play music" in command:
            self.music_player.play_music_thread()
        elif "pause" in command:
            Util.speak("Pausing music...")
            self.music_player.pause_music()
        elif "resume" in command:
            Util.speak("Unpausing music...")
            self.music_player.unpause_music()
        elif "stop" in command:
            Util.speak("Stopping music...")
            self.music_player.stop_music()
        elif any(skip in command for skip in ["next", "skip"]):
            Util.speak("Playing next track...")
            self.music_player.play_next()
        elif "seek forward" in command:
            try:
                seconds = 10
                Util.speak(f"Seeking forward by {seconds} seconds")
                self.music_player.seek_forward(seconds)
            except ValueError:
                Util.speak("Invalid time. Please provide the number of seconds to seek forward.")
        elif "shut down" in command or "shutdown" in command:
            Util.speak("Quitting the program")
            self.stop()
            sys.exit(0)
        elif "play" in command: 
            song_name = command.replace("play", "").strip() # remove the word 'play' from the command, and strip any leading/trailing whitespace
            if song_name:
                subprocess.run(["python", r"pico-files\libs\music_search.py", song_name])
                Util.speak(f"{song_name} will be played shortly...")
                self.music_player.play_music_thread()
        elif any(task in command for task in ["add task", "add a task", "add a new task"]):
            task = Util.speak("Please provide the task!")
            if task:
                Util.speak(f"Adding task: {task}")
                self.task_manager.add_task_at_start(task)
        
        elif any(search in command for search in ["search task", "search for task"]):
            task = Util.speak("Please provide the task to search for!")
            if task:
                Util.speak(f"Searching for task: {task}")
                # Assuming self.task_manager.tasks is a list of task names
                # If tasks are stored differently, adjust the following line accordingly
                tasks = [task.name for task in self.task_manager.display_tasks()]  # Adjust based on actual task list structure
                close_matches = difflib.get_close_matches(task, tasks, n=1, cutoff=0.7)  # Adjust cutoff as needed
                if close_matches:
                    matched_task = close_matches[0]
                    self.task_manager.search_task(matched_task)
                else:
                    Util.speak("No matching task found.")
        else:
            close_matches = difflib.get_close_matches(command, commands, n=1)
            if close_matches:
                closest_match = close_matches[0]
                Util.speak(f"Did you mean '{closest_match}'? Please say yes or no.")
                response = Util.getSpeech()
                if response == "yes":
                    self.process_command(closest_match)
                else:
                    Util.speak("I'm sorry, I didn't understand that command.")
            else:
                Util.speak("I'm sorry, I didn't understand that command.")

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

keyword_path = ""
if platform.system() == "Windows":
    keyword_path = r"pico-files\model\wake-mode\Hey-Fam_en_windows_v3_0_0.ppn"
elif platform.machine() == "armv6l":
    keyword_path = r"pico-files\model\wake-mode\Hey-Fam_en_raspberry-pi_v3_0_0.ppn"

porcupine_listener = PorcupineListener(access_key=access_key, keyword_path=keyword_path)

def main():
    porcupine_listener.run_in_thread()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        porcupine_listener.stop()
        if porcupine_listener.thread is not None:
            porcupine_listener.thread.join()
