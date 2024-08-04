import numpy as np
import pyaudio
import threading
import tkinter as tk
import time

class RGBRingLight:
    def __init__(self, num_pixels: int):
        self.num_pixels = num_pixels
        self.led_states = [(0, 0, 0)] * num_pixels

    def blue_shade(self, intensity: int) -> tuple:
        """Generate shades of blue based on intensity."""
        intensity = max(0, min(255, intensity))
        return (0, 0, intensity)

class Led24BitEffects(RGBRingLight):
    def __init__(self, num_pixels: int = 23):
        super().__init__(num_pixels)
        self.ambient_effect_running = False

    def start_visualizer_effect(self, canvas, leds, stream):
        self.ambient_effect_running = True
        offset = 0
        while self.ambient_effect_running:
            audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)
            volume_norm = np.linalg.norm(audio_data) / 100.0
            brightness = min(int(volume_norm * 255), 255)
            self.visualize_speech(brightness, canvas, leds, offset)
            offset = (offset + 1) % self.num_pixels
            time.sleep(0.05)

    def visualize_speech(self, brightness, canvas, leds, offset):
        num_segments = self.num_pixels // 2
        angle_step = 360 / num_segments

        for i in range(self.num_pixels):
            pos = (i + offset) % self.num_pixels
            angle = (pos * angle_step) % 360
            color = self.blue_shade(brightness)
            if angle <= 180:
                adjusted_color = (color[0], color[1], int(color[2] * (angle / 180)))
            else:
                adjusted_color = (color[0], color[1], int(color[2] * ((360 - angle) / 180)))

            self.led_states[i] = adjusted_color
            color_hex = f'#{adjusted_color[0]:02x}{adjusted_color[1]:02x}{adjusted_color[2]:02x}'
            canvas.itemconfig(leds[i], fill=color_hex)
        canvas.update()

    def stop_ambient_effect(self):
        self.ambient_effect_running = False
        self.clear()

    def clear(self):
        self.led_states = [(0, 0, 0)] * self.num_pixels

def main():
    # Initialize GUI
    root = tk.Tk()
    root.title("LED Visualizer")
    canvas = tk.Canvas(root, width=500, height=100)
    canvas.pack()

    leds = []
    num_pixels = 23
    for i in range(num_pixels):
        led = canvas.create_oval(20*i+5, 10, 20*i+25, 30, fill='black')
        leds.append(led)

    led_effects = Led24BitEffects(num_pixels=num_pixels)

    try:
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        
        print("Simulating visualizer effect. Close the window to stop.")
        
        ambient_thread = threading.Thread(target=led_effects.start_visualizer_effect, args=(canvas, leds, stream))
        ambient_thread.start()

        root.mainloop()
    finally:
        led_effects.stop_ambient_effect()
        if ambient_thread.is_alive():
            ambient_thread.join()
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == '__main__':
    main()
