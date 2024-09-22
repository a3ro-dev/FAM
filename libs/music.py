import os
import random
import threading
import time
import libs.pygame_manager
import pygame
PygameManager = libs.pygame_manager.PygameManager()
import libs.utilities as utilities

# Constants for file extensions
MUSIC_EXTENSIONS = ('.mp3', '.wav')

class MusicPlayer:
    def __init__(self, music_directory: str, shuffle: bool = False):
        self.music_directory = music_directory
        self.shuffle = shuffle
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.lock = threading.Lock()
        self.utils = utilities.Utilities()

    def load_playlist(self) -> list:
        if not os.path.isdir(self.music_directory):
            raise ValueError(f"Invalid directory: {self.music_directory}")
        return [os.path.join(self.music_directory, f) for f in os.listdir(self.music_directory) if f.endswith(MUSIC_EXTENSIONS)]

    def play_music(self):
        with self.lock:
            if not self.playlist:
                print("No music files found in the directory.")
                return
    
            if self.shuffle:
                random.shuffle(self.playlist)
    
            self.is_playing = True
            self.is_paused = False
            self._play_current_song()
    
        while self.is_playing:
            if not PygameManager.is_busy() and not self.is_paused:
                print("Music finished or not playing, moving to next track.")
                self.play_next()
            else:
                print("Music is playing.")
            time.sleep(1)

    def _play_current_song(self):
        try:
            current_song = self.playlist[self.current_index]
            PygameManager.load_and_play(current_song)
            time.sleep(1)  # Add a small delay to ensure the music starts properly
            song_name = os.path.basename(current_song)
            song_name_without_extension = os.path.splitext(song_name)[0]
            now_playing = f"Now Playing: {song_name_without_extension}"
            threading.Thread(target=self.utils.speak, args=(now_playing,)).start()  # Use a separate thread for TTS
            self.is_playing = True
        except pygame.error as e:
            print(f"Error playing music: {e}")
            self.is_playing = False

    def play_music_thread(self):
        if not self.is_playing:
            self.thread = threading.Thread(target=self.play_music)
            self.thread.start()

    def play_next(self):
        with self.lock:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self._play_current_song()

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
            PygameManager.stop()
            if hasattr(self, 'thread') and self.thread is not None:
                self.thread.join()

    def set_volume(self, volume: int):
        if 0 <= volume <= 100:
            PygameManager.set_volume(volume)
        else:
            raise ValueError("Volume must be between 0 and 100")

    def seek_forward(self, seconds: int):
        if self.is_playing:
            current_pos = pygame.mixer.music.get_pos() / 1000
            try:
                pygame.mixer.music.set_pos(current_pos + seconds)
            except pygame.error as e:
                print(f"Error seeking forward: {e}")