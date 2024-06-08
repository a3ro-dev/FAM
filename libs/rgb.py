from rpi_ws281x import PixelStrip, Color
import time
import math

class RGBController:
    def __init__(self, num_pixels, pin=18, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0):
        self.strip = PixelStrip(num_pixels, pin, freq_hz, dma, invert, brightness, channel)
        self.strip.begin()

    def breathe(self, color, duration):
        for i in range(duration * 100):  # 100 steps per second
            brightness = (math.sin(i / 100.0) + 1) / 2  # Calculate brightness (0 to 1)
            for j in range(self.strip.numPixels()):
                self.strip.setPixelColor(j, Color(int(color[0]*brightness), int(color[1]*brightness), int(color[2]*brightness)))
            self.strip.show()
            time.sleep(0.01)

    def processing(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(*color))
            self.strip.show()
            time.sleep(0.1)
            self.strip.setPixelColor(i, Color(0, 0, 0))

    def success(self):
        for _ in range(2):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0, 255, 0))  # Green
            self.strip.show()
            time.sleep(0.5)
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
            time.sleep(0.5)

    def failure(self):
        for _ in range(4):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(255, 0, 0))  # Red
            self.strip.show()
            time.sleep(0.25)
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
            time.sleep(0.25)