import os
import pygame
import random

pygame.init()
class MusicPlayer:
    """
    A class that represents a music player.

    Attributes:
        songs_dir (str): The directory where the music files are located.
        shuffle (bool): A flag indicating whether to shuffle the songs queue.
        songs_queue (list): A list of paths to the music files in the songs directory.
        current_song_index (int): The index of the currently playing song in the songs queue.
        total_songs (int): The total number of songs in the songs queue.

    Methods:
        load_songs(): Loads the music files from the songs directory.
        play_music(): Plays the current song.
        pause_music(): Pauses the currently playing song.
        unpause_music(): Unpauses the currently paused song.
        seek_to(position): Seeks to the specified position in the currently playing song.
        get_music_progress(): Returns the current progress of the currently playing song.
        queue_status(): Returns the status of the songs queue.
        check_for_next_song(): Checks for the next song in the songs queue and plays it if available.
        get_time_left(): Returns the remaining time of the currently playing song.
        get_duration_played(): Returns the duration of the currently playing song that has been played.
    """

    def __init__(self, songs_dir, shuffle=False):
        pygame.mixer.init()
        self.songs_dir = songs_dir
        self.shuffle = shuffle
        self.songs_queue = self.load_songs()
        self.current_song_index = 0
        self.total_songs = len(self.songs_queue)
    
    def load_songs(self):
        """
        Loads the music files from the songs directory.

        Returns:
            list: A list of paths to the music files in the songs directory.
        """
        songs = [os.path.join(self.songs_dir, f) for f in os.listdir(self.songs_dir) if f.endswith('.mp3')]
        if self.shuffle:
            random.shuffle(songs)
        return songs

    def play_music(self):
        """
        Plays the current song.
        """
        if self.songs_queue:
            pygame.mixer.music.load(self.songs_queue[self.current_song_index])
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            self.check_for_next_song()

    def pause_music(self):
        """
        Pauses the currently playing song.
        """
        pygame.mixer.music.pause()

    def unpause_music(self):
        """
        Unpauses the currently paused song.
        """
        pygame.mixer.music.unpause()

    def seek_to(self, position):
        """
        Seeks to the specified position in the currently playing song.

        Args:
            position (float): The position to seek to in seconds.
        """
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(position)

    def get_music_progress(self):
        """
        Returns the current progress of the currently playing song.

        Returns:
            int: The current progress of the currently playing song in milliseconds.
        """
        return pygame.mixer.music.get_pos()

    def queue_status(self):
        """
        Returns the status of the songs queue.

        Returns:
            str: The status of the songs queue in the format "current_song_index/total_songs".
        """
        return f"{self.current_song_index + 1}/{self.total_songs}"

    def check_for_next_song(self):
        """
        Checks for the next song in the songs queue and plays it if available.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:  # Song finished playing
                    self.current_song_index += 1
                    if self.current_song_index < self.total_songs:
                        self.play_music()
                    else:
                        print("End of queue.")
                        return
            pygame.time.wait(1000)  # Check every second

    def get_time_left(self):
        """
        Returns the remaining time of the currently playing song.

        Returns:
            int: The remaining time of the currently playing song in milliseconds.
        """
        if pygame.mixer.music.get_busy():
            # Assuming 4 minutes per song for simplicity, adjust as needed
            duration_ms = 240000
            progress = self.get_music_progress()
            return duration_ms - progress
        return 0

    def get_duration_played(self):
        """
        Returns the duration of the currently playing song that has been played.

        Returns:
            int: The duration of the currently playing song that has been played in milliseconds.
        """
        return self.get_music_progress()
    
    def set_volume(self, volume):
        # Assuming self.player is an instance of a music player library
        # that supports volume control
        pygame.mixer.music.set_volume = volume

# Example usage
mp = MusicPlayer(r'F:\ai-assistant\pico-files\music', shuffle=True) 
