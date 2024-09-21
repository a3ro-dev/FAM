import pygame

class PygameManager:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            pygame.mixer.init(buffer=1024)
            cls._initialized = True

    @classmethod
    def load_and_play(cls, file_path):
        cls.initialize()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    @classmethod
    def stop(cls):
        pygame.mixer.music.stop()

    @classmethod
    def is_busy(cls):
        return pygame.mixer.music.get_busy()

    @classmethod
    def set_volume(cls, volume):
        pygame.mixer.music.set_volume(volume / 100.0)