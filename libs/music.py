import os
import random
import threading
import time
import logging
import libs.pygame_manager as pygame_manager
import libs.utilities as utilities
import difflib

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

        # Initialize mixer and set up end event using pygame_manager
        pygame_manager.PygameManager.initialize()
        pygame_manager.PygameManager.set_end_event()

    def load_playlist(self) -> set:
        if not os.path.isdir(self.music_directory):
            raise ValueError(f"Invalid directory: {self.music_directory}")
        playlist = {os.path.join(self.music_directory, f) for f in os.listdir(self.music_directory) if f.endswith(MUSIC_EXTENSIONS)}
        logging.info("Playlist loaded with %d files", len(playlist))
        return playlist

    def play_music(self):
        with self.lock:
            if not self.playlist:
                logging.warning("No music files found in the directory.")
                return

            if self.shuffle:
                self.playlist = list(self.playlist)
                random.shuffle(self.playlist)
                self.playlist = set(self.playlist)

            self.is_playing = True
            self.is_paused = False
            self._play_current_song()

        while self.is_playing:
            # Wait for events using pygame_manager
            events = pygame_manager.PygameManager.get_events()
            for event in events:
                if event.type == pygame_manager.PygameManager.END_EVENT:
                    logging.info("Song finished, moving to next track.")
                    self.play_next()
            time.sleep(1)

    def _play_current_song(self):
        retries = 2  # Try 3 times to play a song before skipping
        while retries > 0:
            try:
                current_song = list(self.playlist)[self.current_index]
                pygame_manager.PygameManager.load_and_play(current_song)
                time.sleep(1)  # Ensure music starts playing
                song_name = os.path.basename(current_song)
                song_name_without_extension = os.path.splitext(song_name)[0]
                self.set_volume(volume=20)
                now_playing = f"Now Playing: {song_name_without_extension}"
                announcement_thread = threading.Thread(target=self.utils.speak, args=(now_playing,))
                announcement_thread.start()
                announcement_thread.join()  # Wait for the announcement to complete
                self.set_volume(100)
                self.is_playing = True
                logging.info("Playing song: %s", current_song)
                break
            except pygame_manager.PygameManager.PygameError as e:
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
                pygame_manager.PygameManager.pause()
                self.is_paused = True
                logging.info("Music paused.")

    def unpause_music(self):
        with self.lock:
            if self.is_playing and self.is_paused:
                pygame_manager.PygameManager.unpause()
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
            current_pos = pygame_manager.PygameManager.get_position()
            try:
                pygame_manager.PygameManager.set_position(current_pos + seconds)
                logging.info("Seeked forward by %d seconds", seconds)
            except pygame_manager.PygameManager.PygameError as e:
                logging.error("Error seeking forward: %s", e)

    def play_specific_song(self, song_name: str) -> bool:
        """Attempt to play a specific song by name."""
        with self.lock:
            song_list = {os.path.splitext(os.path.basename(song))[0]: song for song in self.playlist}
            if song_name in song_list:
                song_path = song_list[song_name]
            else:
                close_matches = difflib.get_close_matches(song_name, song_list.keys(), n=1, cutoff=0.8)
                if close_matches:
                    song_path = song_list[close_matches[0]]
                else:
                    logging.info(f"Song '{song_name}' not found.")
                    return False
            pygame_manager.PygameManager.load_and_play(song_path)
            self.is_playing = True
            self.is_paused = False
            logging.info("Playing specific song: %s", song_path)
            return True