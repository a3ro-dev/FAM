# This file contains the main code for the assistant
import pyaudio
import struct
import pvporcupine
import threading
import libs.gpt as gpt
Gpt = gpt.Generation()
import libs.music as musicP
import libs.utilities as utilities
import asyncio
# Moved PorcupineListener class definition before its usage
class PorcupineListener:
    def __init__(self, access_key, keyword_path):
        self.thread = None
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.audio_stream = None
        self.is_running = False
        self.keyword_event = threading.Event()

    def init_porcupine(self):
        self.porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])

    def init_audio_stream(self):
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    async def start(self):
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
                    self.keyword_event.set()
                    await self.on_keyword_detected()

    async def on_keyword_detected(self):
        print("Keyword detected!")
        Util.speak("")
        command = Util.getSpeech()
        await self.process_command(command)

    async def process_command(self, command):
        print(f"Processing command: {command}")
        if "how are you" in command or "hi" in command or "hello" in command or "wassup" in command or "what's up" in command:
            reply = Gpt.generate_text_response(f'{command}')
            Util.speak(reply)
        elif "start" in command or "start my day" in command or "good morning" in command:
            await Util.startMyDay()
        elif "music" in command:
            Util.speak("Playing music...")
            music = musicP.MusicPlayer(r'F:\ai-assistant\pico-files\music', shuffle=True)
            music.play_music()

    def stop(self):
        self.is_running = False
        if self.audio_stream is not None:
            self.audio_stream.close()
        if self.porcupine is not None:
            self.porcupine.delete()

    def run_in_thread(self):
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start())
    
        new_loop = asyncio.new_event_loop()
        listener_thread = threading.Thread(target=start_loop, args=(new_loop,))
        listener_thread.start()

# Create instance of PorcupineListener
porcupine_listener = PorcupineListener(access_key="DGN57sdflXC4x5AmT5Q9e0xl7D0fyxSMWjF4um8+aFR3OTLsEE6eZA==", keyword_path=r"F:\ai-assistant\pico-files\model\wake-mode\Hey-Fam_en_windows_v3_0_0.ppn")
# Pass the instance to Utilities
Util = utilities.Utilities(porcupine_listener=porcupine_listener)

def main():
    porcupine_listener.run_in_thread()

if __name__ == "__main__":
    main()
