import subprocess
import os
import logging
import socket
import time
import http.server
import socketserver
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Games:
    """
    A class for managing a simple HTTP game server.

    This class handles the initialization, starting, and stopping of an HTTP server
    for serving browser-based games.

    Attributes:
        status (bool): Current server status.
        dir (str): Directory containing game files.
        process (subprocess.Popen): Server process handle.
        httpd (socketserver.TCPServer): HTTP server instance.
        server_thread (threading.Thread): Thread running the server.
    """

    def __init__(self, status: bool, dir: str):
        """
        Initialize the Games server.

        Args:
            status (bool): Initial server status.
            dir (str): Directory containing game files to serve.
        """
        self.status = status
        self.dir = dir
        self.process = None
        logging.info("Games class initialized with status: %s and directory: %s", status, dir)

    def get_ip_address(self) -> str:
        """
        Get the local IP address of the machine.

        Returns:
            str: Local IP address or '127.0.0.1' if unable to determine.
        """
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

    def play_game(self) -> None:
        """
        Start the game server in a separate thread.
        
        Serves the game directory over HTTP on port 8080.
        Prints the server URL when successfully started.
        """
        try:
            logging.info("Attempting to start the game server...")
            if not os.path.exists(self.dir):
                logging.error("Directory does not exist: %s", self.dir)
                return

            os.chdir(self.dir)
            handler = http.server.SimpleHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", 8080), handler)

            def serve():
                self.httpd.serve_forever()

            self.server_thread = threading.Thread(target=serve)
            self.server_thread.daemon = True
            self.server_thread.start()

            time.sleep(2)  # Give the server time to start
            ip_address = self.get_ip_address()
            port = 8080
            logging.info("Game server running at http://%s:%s", ip_address, port)
            print(f"Game server running at http://{ip_address}:{port}")
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)

    def stop_game(self) -> None:
        """
        Stop the game server.

        Raises:
            Exception: If the server is not running.
        """
        if hasattr(self, 'httpd'):
            try:
                logging.info("Attempting to stop the game server")
                self.httpd.shutdown()
                self.server_thread.join()
                logging.info("Game server stopped successfully.")
            except Exception as e:
                logging.error("Failed to stop the game server: %s", e)
                raise e
        else:
            error_message = 'Game server is not running.'
            logging.error(error_message)
            raise Exception(error_message)

# Example usage
if __name__ == "__main__":
    games = Games(status=False, dir=r'D:\ai-assistant\FAM\misc')
    games.play_game()
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the server when Ctrl+C is pressed
        games.stop_game()
        print("Server stopped.")
