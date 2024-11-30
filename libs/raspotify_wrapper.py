import subprocess
import logging
import time

class RaspotifyWrapper:
    """
    Manages Raspotify operations, including enabling and disabling the service.
    """
    def __init__(self):
        self.is_raspotify_enabled = False

    def enable_raspotify(self):
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