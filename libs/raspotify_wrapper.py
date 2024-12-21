import subprocess
import logging
import time

class RaspotifyWrapper:
    """
    Manages Raspotify operations for controlling the Spotify Connect service on Raspberry Pi.

    This class provides methods to enable and disable the Raspotify service through
    systemctl commands. It maintains the current state of the service and ensures
    idempotent operations.

    Attributes:
        is_raspotify_enabled (bool): Tracks the current state of the Raspotify service
    """
    def __init__(self):
        self.is_raspotify_enabled = False

    def enable_raspotify(self):
        """
        Starts the Raspotify service if it's not already running.

        The method uses systemctl to start the service and updates the internal state.
        Any errors during the process are logged.
        """
        if self.is_raspotify_enabled:
            logging.info("Raspotify is already enabled.")
            return

        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'raspotify'], check=True)
            self.is_raspotify_enabled = True
            logging.info("Raspotify service started.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start Raspotify service: {e}")

    def disable_raspotify(self):
        """
        Stops the Raspotify service if it's currently running.

        The method uses systemctl to stop the service and updates the internal state.
        Any errors during the process are logged.
        """
        if not self.is_raspotify_enabled:
            logging.info("Raspotify is already disabled.")
            return

        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'raspotify'], check=True)
            self.is_raspotify_enabled = False
            logging.info("Raspotify service stopped.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to stop Raspotify service: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bt_manager = RaspotifyWrapper()
    bt_manager.enable_raspotify()
    input("Press Enter to disable Raspotify service...")
    bt_manager.disable_raspotify()