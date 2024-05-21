import os
import pygame
import random

pygame.init()
class MusicPlayer:
    def __init__(self, songs_dir, shuffle=False):
        pygame.mixer.init()
        self.songs_dir = songs_dir
        self.shuffle = shuffle
        self.songs_queue = self.load_songs()
        self.current_song_index = 0
        self.total_songs = len(self.songs_queue)
    
    def load_songs(self):
        # Assuming the implementation of load_songs is to list all mp3 files in the directory
        songs = [os.path.join(self.songs_dir, f) for f in os.listdir(self.songs_dir) if f.endswith('.mp3')]
        if self.shuffle:
            random.shuffle(songs)
        return songs

    def play_music(self):
        if self.songs_queue:
            pygame.mixer.music.load(self.songs_queue[self.current_song_index])
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            self.check_for_next_song()

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def seek_to(self, position):
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(position)

    def get_music_progress(self):
        return pygame.mixer.music.get_pos()

    def queue_status(self):
        return f"{self.current_song_index + 1}/{self.total_songs}"

    def check_for_next_song(self):
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
        if pygame.mixer.music.get_busy():
            # Assuming 4 minutes per song for simplicity, adjust as needed
            duration_ms = 240000
            progress = self.get_music_progress()
            return duration_ms - progress
        return 0

    def get_duration_played(self):
        return self.get_music_progress()
