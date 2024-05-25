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
    """
    A class that listens for a keyword using Porcupine and processes commands based on the detected keyword.

    Args:
        access_key (str): The access key for Porcupine.
        keyword_path (str): The path to the keyword file.

    Attributes:
        thread (Thread): The thread used to run the listener.
        access_key (str): The access key for Porcupine.
        keyword_path (str): The path to the keyword file.
        porcupine (Porcupine): The Porcupine instance.
        audio_stream (AudioStream): The audio stream instance.
        is_running (bool): Flag indicating if the listener is running.

    """

    def __init__(self, access_key, keyword_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False

    def init_porcupine(self):
        """
        Initializes the Porcupine instance.
        """
        self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])

    def init_audio_stream(self):
        """
        Initializes the audio stream.
        """
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
        """
        Starts the listener.
        """
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

    def on_keyword_detected(self):
        """
        Callback function when a keyword is detected.
        """
        print("Keyword detected!")
        Util.speak("Keyword detected. Listening for your command...")
        command = Util.getSpeech()
        print(f"Recognized command: {command}")
        self.process_command(command)

    def process_command(self, command):
        """
        Processes the command based on the detected keyword.

        Args:
            command (str): The command to process.
        """
        print(f"Processing command: {command}")
        if "how are you" in command or "hi" in command or "hello" in command or "wassup" in command or "what's up" in command:
            reply = str(Gpt.generate_text_response(f'{command}'))
            Util.speak(reply)
        elif "time" in command or "what time is it" in command or "current time" in command:
            Util.speak(Util.getTime())
        elif "vision" in command or "eyes" in command:
            Util.speak("Let me have a look....")
            Util.captureImage()
            reply = str(Gpt.generate_text_with_image(f"{command}", r"F:\ai-assistant\pico-files\assets\image.jpg"))
            Util.playChime('load')

        elif "start" in command or "start my day" in command or "good morning" in command:
            Util.startMyDay()
        elif "music" in command:
            Util.speak("Playing music...")
            music = musicP.MusicPlayer(r'F:\ai-assistant\pico-files\music', shuffle=True)
            music.play_music()
        
        elif "stop" in command:
            Util.speak("Quitting the program")
            sys.exit(0)
        else:
            Util.speak("I'm sorry, I didn't understand that command.")

    def stop(self):
        """
        Stops the listener.
        """
        self.is_running = False
        if self.audio_stream is not None:
            self.audio_stream.close()
        if self.porcupine is not None:
            self.porcupine.delete()

    def run_in_thread(self):
        """
        Runs the listener in a separate thread.
        """
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

# Create instance of PorcupineListener
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

