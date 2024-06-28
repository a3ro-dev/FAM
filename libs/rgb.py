import board #type: ignore
import neopixel #type: ignore
import time
import math
import random
import threading

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
        self.ambient_effect_running = False
        self.effect_running = False

    def start_ambient_effect(self):
        self.ambient_effect_running = True
        while self.ambient_effect_running:
            self.blue_breathing_effect()  # Example ambient effect

    def stop_ambient_effect(self):
        self.ambient_effect_running = False

    def blue_breathing_effect(self, duration=10):
        start_time = time.time()
        while self.ambient_effect_running and (time.time() - start_time < duration):
            brightness = (math.sin((time.time() % 1) * 2 * math.pi) + 1) / 2
            blue_value = int(255 * brightness)

            for i in range(self.num_pixels):
                self.pixels[i] = (0, 0, blue_value)
            self.pixels.show()

            time.sleep(0.01)

        if not self.ambient_effect_running:
            for i in range(self.num_pixels):
                self.pixels[i] = (0, 0, 0)
            self.pixels.show()

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


    def start_progress_effect(self, song_duration):
        self.effect_running = True
        effect_thread = threading.Thread(target=self._progress_effect, args=(song_duration,))
        effect_thread.start()

    def _progress_effect(self, song_duration):
        start_time = time.time()
        while self.effect_running:
            elapsed_time = time.time() - start_time
            leds_to_light = int((elapsed_time / song_duration) * self.num_pixels)
            for i in range(self.num_pixels):
                if i < leds_to_light:
                    self.pixels[i] = (255, 255, 255)  # Example: light up in white
                else:
                    self.pixels[i] = (0, 0, 0)  # Turn off the LED
            self.pixels.show()
            if elapsed_time >= song_duration:
                break  # Optional: Stop the effect when the song duration is reached
            time.sleep(10)  # Update every 10 seconds

    def stop_effect(self):
        self.effect_running = False
        # Optional: Turn off all LEDs when stopping the effect
        for i in range(self.num_pixels):
            self.pixels[i] = (0, 0, 0)
        self.pixels.show()

def run_effect_for_duration(effect_function, duration, *args, **kwargs):
    effect_thread = threading.Thread(target=effect_function, args=args, kwargs=kwargs)
    effect_thread.start()
    time.sleep(duration)
    if hasattr(effect_function.__self__, 'stop_ambient_effect'):
        effect_function.__self__.stop_ambient_effect()
    if hasattr(effect_function.__self__, 'stop_effect'):
        effect_function.__self__.stop_effect()
    effect_thread.join()

if __name__ == "__main__":
    ring_light = Led24BitEffects()

    # List of effects to run
    effects = [
        (ring_light.blue_breathing_effect, {'duration': 5}),
        (ring_light.firefly, {'wait': 0.05, 'duration': 5}),
        (ring_light.rainbow_cycle, {'wait': 0.05}),
        (ring_light.gradient, {'wait': 5}),
        (ring_light.bouncing_ball, {'wait': 0.05}),
        (ring_light.comet, {'wait': 0.05}),
        (ring_light.vortex, {'wait': 0.05}),
        (ring_light.start_progress_effect, {'song_duration': 5})
    ]
for effect, kwargs in effects:
    # Check if 'duration' is in kwargs, use it; otherwise, use 5 as the default duration
    duration = kwargs.pop('duration', 5)
    print(f"Activating effect: {effect.__name__}")
    run_effect_for_duration(effect, duration, **kwargs)