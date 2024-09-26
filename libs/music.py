import os
import random
import threading
import time
import logging
import pygame
import libs.pygame_manager as pygame_manager
import libs.utilities as utilities

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.thread = None
        logging.info("MusicPlayer initialized with directory: %s", music_directory)

    def load_playlist(self) -> list:
        if not os.path.isdir(self.music_directory):
            raise ValueError(f"Invalid directory: {self.music_directory}")
        playlist = [os.path.join(self.music_directory, f) for f in os.listdir(self.music_directory) if f.endswith(MUSIC_EXTENSIONS)]
        logging.info("Playlist loaded with %d files", len(playlist))
        return playlist

    def play_music(self):
        with self.lock:
            if not self.playlist:
                logging.warning("No music files found in the directory.")
                return

            if self.shuffle:
                random.shuffle(self.playlist)

            self.is_playing = True
            self.is_paused = False
            self._play_current_song()

        while self.is_playing:
            with self.lock:
                # Ensure the music has finished playing before moving to the next song
                if not pygame.mixer.music.get_busy() and not self.is_paused:
                    logging.info("Music finished, moving to next track.")
                    self.play_next()
                else:
                    logging.debug("Music is still playing or paused.")
            time.sleep(1)  # Give the loop a small delay to avoid high CPU usage

    def _play_current_song(self):
        retries = 3  # Try 3 times to play a song before skipping
        while retries > 0:
            try:
                current_song = self.playlist[self.current_index]
                pygame_manager.PygameManager.load_and_play(current_song)
                time.sleep(1)  # Ensure music starts playing
                song_name = os.path.basename(current_song)
                song_name_without_extension = os.path.splitext(song_name)[0]
                self.set_volume(volume=20)
                time.sleep(0.5)
                now_playing = f"Now Playing: {song_name_without_extension}"
                time.sleep(0.5)
                self.set_volume(100)
                threading.Thread(target=self.utils.speak, args=(now_playing,)).start()  # Announce now playing song
                self.is_playing = True
                logging.info("Playing song: %s", current_song)
                break
            except pygame.error as e:
                logging.error("Error playing music: %s. Retries left: %d", e, retries)
                retries -= 1
                time.sleep(1)  # Short delay before retrying
                if retries == 0:
                    logging.error("Failed to play the song. Skipping to next.")
                    self.play_next()

    def play_music_thread(self):
        if not self.is_playing:
            self.thread = threading.Thread(target=self.play_music)
            self.thread.start()
            logging.info("Music playback thread started.")

    def play_next(self):
        with self.lock:
            # Move to the next song or loop back if it's the end of the playlist
            self.current_index = (self.current_index + 1) % len(self.playlist)
            logging.info("Moving to next song: index %d", self.current_index)
            self._play_current_song()

    def pause_music(self):
        with self.lock:
            if self.is_playing and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                logging.info("Music paused.")

    def unpause_music(self):
        with self.lock:
            if self.is_playing and self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                logging.info("Music unpaused.")

    def stop_music(self):
        with self.lock:
            self.is_playing = False
            pygame_manager.PygameManager.stop()
            if self.thread is not None:
                self.thread.join()
                self.thread = None
            logging.info("Music stopped.")

    def set_volume(self, volume: int):
        if 0 <= volume <= 100:
            pygame_manager.PygameManager.set_volume(volume)
            logging.info("Volume set to %d", volume)
        else:
            raise ValueError("Volume must be between 0 and 100")

    def seek_forward(self, seconds: int):
        if self.is_playing:
            current_pos = pygame.mixer.music.get_pos() / 1000
            try:
                pygame.mixer.music.set_pos(current_pos + seconds)
                logging.info("Seeked forward by %d seconds", seconds)
            except pygame.error as e:
                logging.error("Error seeking forward: %s", e)