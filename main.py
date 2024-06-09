import pyaudio
import struct
import pvporcupine
import threading
import libs.gpt as gpt
import libs.music as musicP
import libs.utilities as utilities
import sys
import platform
import difflib
import yaml

Gpt = gpt.Generation()
Util = utilities.Utilities()

with open('/home/pi/FAM/pico-files/conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

access_key = config['main']['access_key']
keyword_path = config['main']['keyword_path']
music_path = config['main']['music_path']

commands = {"how are you", "hi", "hello", "wassup", "what's up", "hey", "sup", "time", "what time is it", "current time", "date", "what's the date", "current date", "vision", "eyes", "start", "start my day", "good morning", "news", "daily news", "what's happening", "what's the news", "play music", "pause", "resume", "stop", "next", "skip", "seek forward", "shut down"}

class PorcupineListener:
    def __init__(self, access_key, keyword_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.music_player = musicP.MusicPlayer(music_path, shuffle=True)

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
        Util.speak("Keyword detected. Listening for your command...")
        if self.music_player.is_playing:
            self.music_player.set_volume(20)
        try:
            command = Util.getSpeech()
        except Exception as e:
            print(f"Error in speech recognition {e}")
            return
        print(f"Recognized command: {command}")
        if self.music_player.is_playing and command != "stop music":
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
            Util.speak("Playing music...")
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
    keyword_path = r"F:\ai-assistant\pico-files\model\wake-mode\Hey-Fam_en_windows_v3_0_0.ppn"
elif platform.machine() == "armv6l":
    keyword_path = "/home/pi/FAM/pico-files/model/wake-mode/Hey-Fam_en_raspberry-pi_v3_0_0.ppn"

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
