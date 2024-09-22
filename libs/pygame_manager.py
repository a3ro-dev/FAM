import pygame

class PygameManager:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            print("Initializing pygame mixer...")
            pygame.mixer.init(buffer=1024)
            cls._initialized = True
            print("Pygame mixer initialized.")

    @classmethod
    def load_and_play(cls, file_path):
        cls.initialize()
        print(f"Loading and playing file: {file_path}")
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("Music started playing.")

    @classmethod
    def stop(cls):
        print("Stopping music.")
        pygame.mixer.music.stop()

    @classmethod
    def is_busy(cls):
        busy = pygame.mixer.music.get_busy()
        print(f"Music is busy: {busy}")
        return busy

    @classmethod
    def set_volume(cls, volume):
        print(f"Setting volume to: {volume}")
        pygame.mixer.music.set_volume(volume / 100.0)