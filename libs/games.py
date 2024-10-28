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

    def get_ip_address(self):
        """Get the IP address of the machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Attempt to connect to a non-existent IP to determine local IP.
            s.connect(('10.254.254.254', 1))
            ip_address = s.getsockname()[0]
        except Exception as e:
            logging.error("Failed to get IP address: %s", e)
            ip_address = '127.0.0.1'
        finally:
            s.close()
        return ip_address

    def play_game(self):
        try:
            logging.info("Attempting to start the game server...")
            if not os.path.exists(self.dir):
                logging.error("Directory does not exist: %s", self.dir)
                return

            self.process = subprocess.Popen(
                ['python3', '-m', 'http.server', '8080'],
                cwd=self.dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Give the server time to start
            ip_address = self.get_ip_address()
            port = 8080
            if self.process.poll() is None:  # Check if the process is still running
                logging.info("Game server started with PID: %s", self.process.pid)
                logging.info("Game server running at http://%s:%s", ip_address, port)
                print(f"Game server running at http://{ip_address}:{port}")
            else:
                stdout, stderr = self.process.communicate()
                logging.error("Failed to start the game server. stdout: %s, stderr: %s", stdout.decode(), stderr.decode())
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

# Example usage
if __name__ == "__main__":
    games = Games(status=False, dir='/path/to/your/game/directory')
    games.play_game()
    time.sleep(10)  # Keep the server running for 10 seconds for demonstration
    games.stop_game()