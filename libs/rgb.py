import board #type: ignore
import neopixel #type: ignore
import time
import math
import random

class RGBRingLight:
    def __init__(self, pixel_pin, num_pixels, brightness=0.3, pixel_order=neopixel.GRB):
        self.num_pixels = num_pixels
        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=brightness, auto_write=False, pixel_order=pixel_order
        )

    def wheel(self, pos):
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
    def __init__(self, pixel_pin=board.D18, num_pixels=24, brightness=0.3, pixel_order=neopixel.GRB):
        super().__init__(pixel_pin, num_pixels, brightness, pixel_order)

    def firefly(self, wait, duration=5):
        start_time = time.time()
        for i in range(self.num_pixels):
            self.pixels[i] = (0, 0, 0)
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

    def rainbow_cycle(self, wait):
        for j in range(255):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + j
                self.pixels[i] = self.wheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(wait)

    def gradient(self, wait):
        for i in range(self.num_pixels):
            color = self.wheel((i * 256 // self.num_pixels) & 255)
            self.pixels[i] = color
        self.pixels.show()
        time.sleep(wait)

    def bouncing_ball(self, wait):
        for j in range(5):
            for i in range(self.num_pixels):
                self.pixels[i] = (0, 0, 0)
            pos = int((math.sin(j + time.time()) + 1) * (self.num_pixels - 1) / 2)
            self.pixels[pos] = (255, 255, 255)
            self.pixels.show()
            time.sleep(wait)

    def comet(self, wait):
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

    def vortex(self, wait):
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

def main():
    led_effects = Led24BitEffects()
    start_time = time.time()  # get the current time

    while True:
        if time.time() - start_time < 5:
            led_effects.bouncing_ball(0.05)
        elif time.time() - start_time < 10:
            led_effects.comet(0.02)
        elif time.time() - start_time < 15:
            led_effects.vortex(0.01)
        elif time.time() - start_time < 20:
            led_effects.firefly(5/255.0)  # adjust the wait time to ensure the effect lasts approximately 5 seconds
        else:
            start_time = time.time()  # reset the start time

if __name__ == "__main__":
    main()