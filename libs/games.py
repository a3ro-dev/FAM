import subprocess
import time
import os
import signal

class Games:
    def __init__(self, status: bool, dir: str):
        self.status = status
        self.dir = dir
        self.process = None

    def play_game(self):
        try:
            self.process = subprocess.Popen(['/home/pi/FAM/env/bin/python3', '-m', 'http.server', '8080'], cwd=self.dir, shell=True)
        except Exception as e:
            return e

    def stop_game(self):
        if self.process:
            try:
                os.kill(self.process.pid, signal.SIGTERM)
            except Exception as e:
                return e
        else:
            raise Exception('Games not installed')

