import os
import random
import threading
import time
import pygame
import libs.utilities as utilities

# Constants for file extensions
MUSIC_EXTENSIONS = ('.mp3', '.wav')

class MusicPlayer:
    """
    A class that represents a music player.

    Attributes:
        music_directory (str): The directory where the music files are located.
        shuffle (bool): A flag indicating whether to shuffle the playlist.
        playlist (list): A list of music files in the directory.
        current_index (int): The index of the currently playing music in the playlist.
        is_playing (bool): A flag indicating whether music is currently playing.
        is_paused (bool): A flag indicating whether music is currently paused.
        lock (threading.Lock): A lock to synchronize access to shared resources.
        utils (utilities.Utilities): An instance of the Utilities class.
        rgb_control (rgb.Led24BitEffects): An instance of the RGB control class.

    Methods:
        load_playlist(): Loads the playlist by scanning the music directory.
        play_music(): Plays the music from the playlist.
        play_music_thread(): Starts a new thread to play the music.
        play_next(): Plays the next music in the playlist.
        pause_music(): Pauses the currently playing music.
        unpause_music(): Unpauses the currently paused music.
        stop_music(): Stops the currently playing music.
        set_volume(volume: int): Sets the volume of the music player.
        seek_forward(seconds: int): Seeks forward in the currently playing music.
    """

    def __init__(self, music_directory: str, shuffle: bool = False):
        pygame.mixer.init(buffer=1024)  # Default is 3072, reduce it or increase it depending on performance
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
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                self.play_next()
            time.sleep(1)

    def _play_current_song(self):
        try:
            current_song = self.playlist[self.current_index]
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.play()
            song_name = os.path.basename(current_song)
            song_name_without_extension = os.path.splitext(song_name)[0]
            now_playing = f"Now Playing: {song_name_without_extension}"
            self.utils.speak(now_playing)
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
            pygame.mixer.music.stop()
            if hasattr(self, 'thread') and self.thread is not None:
                self.thread.join()

    def set_volume(self, volume: int):
        if 0 <= volume <= 100:
            pygame.mixer.music.set_volume(volume / 100.0)
        else:
            raise ValueError("Volume must be between 0 and 100")

    def seek_forward(self, seconds: int):
        if self.is_playing:
            current_pos = pygame.mixer.music.get_pos() / 1000
            try:
                pygame.mixer.music.set_pos(current_pos + seconds)
            except pygame.error as e:
                print(f"Error seeking forward: {e}")