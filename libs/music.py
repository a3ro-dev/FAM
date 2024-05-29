import os
import random
import threading
import time
import pygame

class MusicPlayer:
    def __init__(self, music_directory, shuffle=False):
        self.music_directory = music_directory
        self.shuffle = shuffle
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.thread = None
        pygame.mixer.init()

    def load_playlist(self):
        return [os.path.join(self.music_directory, f) for f in os.listdir(self.music_directory) if f.endswith(('.mp3', '.wav'))]

    def play_music(self):
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
            if not pygame.mixer.music.get_busy():
                self.play_next()
            time.sleep(1)

    def play_music_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.play_music)
            self.thread.start()

    def play_next(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()

    def pause_music(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def unpause_music(self):
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def stop_music(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        if self.thread is not None:
            self.thread.join()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100.0)

    def seek_forward(self, seconds):
        if self.is_playing:
            pygame.mixer.music.set_pos(pygame.mixer.music.get_pos() / 1000.0 + seconds)
