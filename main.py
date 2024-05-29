import pyaudio
import struct
import pvporcupine
import threading
import libs.gpt
import libs.music as musicP
import libs.utilities as utilities
import sys

Gpt = libs.gpt.Generation()
Util = utilities.Utilities()

class PorcupineListener:
    def __init__(self, access_key, keyword_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.music_player = musicP.MusicPlayer(r'F:\ai-assistant\pico-files\music', shuffle=True)

    def init_porcupine(self):
        self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])

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
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
    
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.on_keyword_detected()
                    print("Listening for keyword...")

    def on_keyword_detected(self):
        print("Keyword detected!")
        Util.speak("Keyword detected. Listening for your command...")
        command = Util.getSpeech()
        print(f"Recognized command: {command}")
        self.process_command(command)

    def process_command(self, command):
        print(f"Processing command: {command}")
        if "how are you" in command or "hi" in command or "hello" in command or "wassup" in command or "what's up" in command or "hey" in command or "sup" in command:
            for _ in range(10):
                reply = str(Gpt.live_chat_with_ai(str(command)))
                Util.speak(reply)
                command = Util.getSpeech()
                if command is not None and ("bye" in command or "goodbye" in command or "stop" in command):
                    Util.speak("Goodbye! Have a nice day.")
                    break
        elif "time" in command or "what time is it" in command or "current time" in command:
            Util.speak(Util.getTime())
        elif "date" in command or "what's the date" in command or "current date" in command:
            Util.speak(Util.getDate())
        elif "vision" in command or "eyes" in command:
            Util.captureImage()
            reply = str(Gpt.generate_text_with_image(f"{command}", r"F:\ai-assistant\pico-files\assets\image.jpg"))
            Util.playChime('load')
            Util.speak(reply)
        elif "start" in command or "start my day" in command or "good morning" in command:
            Util.startMyDay()
        elif "date" in command or "what's the date" in command or "current date" in command:
            Util.speak(Util.getDate())
        elif "news" in command or "daily news" in command or "what's happening" in command or "what's the news" in command:
            Util.speak("Here are the top news headlines...")
            news = Util.getNews()
            for headline in news:
                Util.speak(headline)
        # elif "play music" in command:
        #     Util.speak("Playing music...")
        #     self.music_player.play_music_thread()
        # elif "pause music" in command:
        #     Util.speak("Pausing music...")
        #     self.music_player.pause_music()
        # elif "unpause music" in command:
        #     Util.speak("Unpausing music...")
        #     self.music_player.unpause_music()
        # elif "stop music" in command:
        #     Util.speak("Stopping music...")
        #     self.music_player.stop_music()
        # elif "next music" in command or "skip music" in command:
        #     Util.speak("Playing next track...")
        #     self.music_player.play_next()
        # elif "set volume" in command:
        #     try:
        #         volume = int(command.split()[-1])
        #         Util.speak(f"Setting volume to {volume}")
        #         self.music_player.set_volume(volume)
        #     except ValueError:
        #         Util.speak("Invalid volume level. Please provide a number between 1 and 100.")
        # elif "seek forward" in command:
        #     try:
        #         seconds = int(command.split()[-1])
        #         Util.speak(f"Seeking forward by {seconds} seconds")
        #         self.music_player.seek_forward(seconds)
        #     except ValueError:
        #         Util.speak("Invalid time. Please provide the number of seconds to seek forward.")
        elif "stop" in command:
            Util.speak("Quitting the program")
            self.stop()
            sys.exit(0)
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

porcupine_listener = PorcupineListener(access_key="DGN57sdflXC4x5AmT5Q9e0xl7D0fyxSMWjF4um8+aFR3OTLsEE6eZA==",
                                       keyword_path=r"F:\ai-assistant\pico-files\model\wake-mode\Hey-Fam_en_windows_v3_0_0.ppn")

def main():
    porcupine_listener.run_in_thread()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        porcupine_listener.stop()
        if porcupine_listener.thread is not None:
            porcupine_listener.thread.join()
