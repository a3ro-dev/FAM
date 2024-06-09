import os
import random
import threading
import time
import pygame

class MusicPlayer:
    def __init__(self, music_directory, shuffle=False):
        pygame.mixer.init()
        self.music_directory = music_directory
        self.shuffle = shuffle
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.lock = threading.Lock()

    def load_playlist(self):
        return [os.path.join(self.music_directory, f) for f in os.listdir(self.music_directory) if f.endswith(('.mp3', '.wav'))]

    def play_music(self):
        with self.lock:
            if not self.playlist:
                print("No music files found in the directory.")
                return

            if self.shuffle:
                random.shuffle(self.playlist)

            self.is_playing = True
            self.is_paused = False
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.play()

        while self.is_playing:
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                self.play_next()
            time.sleep(1)

    def play_music_thread(self):
        if not self.is_playing:
            self.thread = threading.Thread(target=self.play_music)
            self.thread.start()

    def play_next(self):
        with self.lock:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.play()

    def pause_music(self):
        with self.lock:
            if self.is_playing and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True

    def unpause_music(self):
        with self.lock:
            if self.is_playing and self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False

    def stop_music(self):
        with self.lock:
            self.is_playing = False
            pygame.mixer.music.stop()
            if self.thread is not None:
                self.thread.join()

    def set_volume(self, volume: int):
        pygame.mixer.music.set_volume(volume / 100.0)  # pygame uses a scale of 0.0 to 1.0

    def seek_forward(self, seconds):
        if self.is_playing:
            current_pos = pygame.mixer.music.get_pos() / 1000
            pygame.mixer.music.set_pos(current_pos + seconds)

def main():
    music = MusicPlayer(r"F:\ai-assistant\pico-files\music", shuffle=True)
    
    # Using a separate thread to listen for commands
    def command_listener():
        while True:
            command = input("Enter a command: ")
            if command == "play music":
                music.play_music_thread()
            elif command == "pause":
                music.pause_music()
            elif command == "unpause":
                music.unpause_music()
            elif command == "stop":
                music.stop_music()
            elif command == "next":
                music.play_next()
            elif command.startswith("set volume"):
                _, volume = command.split()
                music.set_volume(int(volume))
            elif command.startswith("seek forward"):
                _, seconds = command.split()
                music.seek_forward(int(seconds))

    command_thread = threading.Thread(target=command_listener, daemon=True)
    command_thread.start()
    command_thread.join()  # Ensuring the main thread waits for command thread to complete

if __name__ == "__main__":
    main()
