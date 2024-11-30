import pygame
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class PygameManager:
    """
    PygameManager is a utility class for managing pygame's mixer module. It provides methods to initialize the mixer,
    load and play music files, stop the music, check if the music is currently playing, and set the volume.
    Class Methods:
        initialize(cls):
            Initializes the pygame mixer if it hasn't been initialized yet. Logs the initialization process.
        load_and_play(cls, file_path):
            Loads a music file from the given file path and starts playing it. Initializes the mixer if necessary.
            Logs the loading and playing process.
        stop(cls):
            Stops the currently playing music. Logs the stopping process.
        is_busy(cls):
            Checks if the music is currently playing. Logs the busy status and returns a boolean.
        set_volume(cls, volume):
            Sets the volume of the music. The volume should be provided as a percentage (0-100).
            Logs the volume setting process.
    """
    _initialized = False

    END_EVENT = pygame.USEREVENT  # Define custom event for song end
    PygameError = pygame.error    # Alias for pygame.error

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            logging.info("Initializing pygame mixer...")
            pygame.init()
            pygame.mixer.init(buffer=1024)
            cls._initialized = True
            logging.info("Pygame mixer initialized.")

    @classmethod
    def load_and_play(cls, file_path):
        if not cls._initialized:
            cls.initialize()
        logging.info(f"Loading and playing file: {file_path}")
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        logging.info("Music started playing.")

    @classmethod
    def set_end_event(cls):
        pygame.mixer.music.set_endevent(cls.END_EVENT)
        logging.info("Music end event set.")

    @classmethod
    def get_events(cls):
        return pygame.event.get()

    @classmethod
    def pause(cls):
        pygame.mixer.music.pause()
        logging.info("Music paused.")

    @classmethod
    def unpause(cls):
        pygame.mixer.music.unpause()
        logging.info("Music unpaused.")

    @classmethod
    def get_position(cls):
        pos = pygame.mixer.music.get_pos() / 1000.0  # Convert milliseconds to seconds
        logging.info(f"Current music position: {pos} seconds")
        return pos

    @classmethod
    def set_position(cls, pos_in_seconds):
        pygame.mixer.music.play(start=pos_in_seconds)
        logging.info(f"Music position set to {pos_in_seconds} seconds")

    @classmethod
    def stop(cls):
        logging.info("Stopping music.")
        pygame.mixer.music.stop()

    @classmethod
    def is_busy(cls):
        busy = pygame.mixer.music.get_busy()
        logging.info(f"Music is busy: {busy}")
        return busy

    @classmethod
    def set_volume(cls, volume):
        logging.info(f"Setting volume to: {volume}")
        pygame.mixer.music.set_volume(volume / 100.0)