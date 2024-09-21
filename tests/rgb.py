import board  # type: ignore
import neopixel  # type: ignore
import time
import math
import random
import threading
import numpy as np

class RGBRingLight:
    def __init__(self, pixel_pin, num_pixels: int, brightness: float = 0.3, pixel_order=neopixel.GRB):
        self.num_pixels = num_pixels
        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=pixel_order
        )

    def wheel(self, pos: int) -> tuple:
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

class Led24BitEffects(RGBRingLight):
    def __init__(self, pixel_pin=board.D18, num_pixels: int = 23, brightness: float = 0.3, pixel_order=neopixel.GRB):
        super().__init__(pixel_pin, num_pixels, brightness, pixel_order)
        self.ambient_effect_running = False
        self.effect_running = False

    def start_visualizer_effect(self, stream):
        self.ambient_effect_running = True
        offset = 0
        while self.ambient_effect_running:
            audio_data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
            volume_norm = np.linalg.norm(audio_data) / 100.0
            brightness = min(int(volume_norm * 255), 255)
            self.visualize_speech(brightness, offset)
            offset = (offset + 1) % self.num_pixels
            time.sleep(0.05)

    def visualize_speech(self, brightness, offset):
        for i in range(self.num_pixels):
            pos = (i + offset) % self.num_pixels
            color = self.blue_shade(brightness)
            self.pixels[pos] = color
        self.pixels.show()

    def blue_shade(self, intensity):
        """Generate shades of blue based on intensity."""
        intensity = max(0, min(255, intensity))
        return (0, 0, intensity)

    def stop_ambient_effect(self):
        self.ambient_effect_running = False
        self.clear()

    def clear(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def start_ambient_effect(self) -> None:
        self.ambient_effect_running = True
        ambient_thread = threading.Thread(target=self.blue_breathing_effect)
        ambient_thread.start()

    def blue_breathing_effect(self, duration: int = 10) -> None:
        start_time = time.time()
        while self.ambient_effect_running and (time.time() - start_time < duration):
            brightness = (math.sin((time.time() % 1) * 2 * math.pi) + 1) / 2
            blue_value = int(255 * brightness)
            self.pixels.fill((0, 0, blue_value))
            self.pixels.show()
            time.sleep(0.01)
        self.clear()

    def alexa_listening_effect(self, duration: int = 10) -> None:
        self.ambient_effect_running = True
        start_time = time.time()
        while self.ambient_effect_running and (time.time() - start_time < duration):
            for i in range(self.num_pixels):
                if not self.ambient_effect_running:
                    break
                self.pixels.fill((0, 0, 0))  # Turn off all pixels
                self.pixels[i] = (0, 0, 255)  # Blue color for Alexa effect
                if i > 0:
                    self.pixels[i - 1] = (0, 0, 128)  # Dimmer blue
                else:
                    self.pixels[self.num_pixels - 1] = (0, 0, 128)  # Dimmer blue
                self.pixels.show()
                time.sleep(0.1)
        self.clear()

    def rotatory_fill(self, color: tuple, wait: float = 0.05) -> None:
        for i in range(self.num_pixels):
            self.pixels.fill((0, 0, 0))
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(wait)

    def firefly(self, wait: float, duration: int = 5) -> None:
        start_time = time.time()
        self.clear()
        while time.time() - start_time < duration:
            index = random.randint(0, self.num_pixels - 1)
            for j in range(255):
                if time.time() - start_time >= duration:
                    return
                self.pixels[index] = (j, j // 2, 0)
                self.pixels.show()
                time.sleep(wait / 1000.0)
            for j in range(255, -1, -1):
                if time.time() - start_time >= duration:
                    return
                self.pixels[index] = (j, j // 2, 0)
                self.pixels.show()
                time.sleep(wait / 1000.0)

    def rainbow_cycle(self, wait: float) -> None:
        for j in range(255):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + j
                self.pixels[i] = self.wheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(wait)

    def gradient(self, wait: float) -> None:
        for i in range(self.num_pixels):
            color = self.wheel((i * 256 // self.num_pixels) & 255)
            self.pixels[i] = color
        self.pixels.show()
        time.sleep(wait)

    def bouncing_ball(self, wait: float) -> None:
        for j in range(5):
            self.clear()
            pos = int((math.sin(j + time.time()) + 1) * (self.num_pixels - 1) / 2)
            self.pixels[pos] = (255, 255, 255)
            self.pixels.show()
            time.sleep(wait)

    def comet(self, wait: float) -> None:
        tail_length = 10
        for i in range(self.num_pixels * 2):
            for j in range(self.num_pixels):
                if i - j < 0 or i - j >= tail_length:
                    self.pixels[j] = (0, 0, 0)
                else:
                    fade = 1 - (i - j) / tail_length
                    color = self.wheel((i * 256 // self.num_pixels) & 255)
                    self.pixels[j] = (
                        int(max(0, min(255, color[0] * fade))),
                        int(max(0, min(255, color[1] * fade))),
                        int(max(0, min(255, color[2] * fade)))
                    )
            self.pixels.show()
            time.sleep(wait)

    def vortex(self, wait: float) -> None:
        for j in range(255):
            for i in range(self.num_pixels):
                angle = (i * 360 / self.num_pixels + j) % 360
                radius = (j % 100) / 100.0
                color = self.wheel(int((angle * 256 // self.num_pixels + j)) & 255)
                self.pixels[i] = (
                    int(max(0, min(255, color[0] * radius))),
                    int(max(0, min(255, color[1] * radius))),
                    int(max(0, min(255, color[2] * radius)))
                )
            self.pixels.show()
            time.sleep(wait)

    def start_progress_effect(self, song_duration: int) -> None:
        self.effect_running = True
        effect_thread = threading.Thread(target=self._progress_effect, args=(song_duration,))
        effect_thread.start()

    def _progress_effect(self, song_duration: int) -> None:
        start_time = time.time()
        while self.effect_running:
            elapsed_time = time.time() - start_time
            leds_to_light = int((elapsed_time / song_duration) * self.num_pixels)
            for i in range(self.num_pixels):
                if i < leds_to_light:
                    self.pixels[i] = (255, 255, 255)
                else:
                    self.pixels[i] = (0, 0, 0)
            self.pixels.show()
            if elapsed_time >= song_duration:
                break
            time.sleep(5)
        self.clear()

    def stop_effect(self) -> None:
        self.effect_running = False
        self.clear()