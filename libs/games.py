import subprocess
import os
import logging
import socket
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Games:
    def __init__(self, status: bool, dir: str):
        self.status = status
        self.dir = dir
        self.process = None
        logging.info("Games class initialized with status: %s and directory: %s", status, dir)

    def play_game(self):
        try:
            logging.info("Attempting to start the game server...")
            self.process = subprocess.Popen(
                ['python', '-m', 'http.server', '8080'],
                cwd=self.dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Give the server time to start
            ip_address = None
            port = 8080
            logging.info("Game server started with PID: %s", self.process.pid)
            logging.info("Game server running at http://%s:%s", ip_address, port)
            print(f"Game server running at http://{ip_address}:{port}")
        except FileNotFoundError as e:
            logging.error("Failed to start the game server: %s", e)
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)

    def stop_game(self):
        if self.process:
            try:
                logging.info("Attempting to stop the game server with PID: %s", self.process.pid)
                self.process.terminate()
                self.process.wait()
                logging.info("Game server stopped successfully.")
            except Exception as e:
                logging.error("Failed to stop the game server: %s", e)
                return e
        else:
            error_message = 'Game server is not running.'
            logging.error(error_message)
            raise Exception(error_message)

