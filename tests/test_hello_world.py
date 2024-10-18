import RPi.GPIO as GPIO
import time
import threading
import logging
import numpy as np
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestureModule:
    def __init__(self, trigger_pin=18, echo_pin=24, distance_range=(2, 5), gesture_interval=0.2, debounce_time=1.0):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.distance_range = distance_range
        self.gesture_interval = gesture_interval
        self.debounce_time = debounce_time
        self.distance_history = deque(maxlen=3)  # Shorter moving average window
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, False)  # Ensure trigger pin is off

    def cleanup_gpio(self):
        GPIO.cleanup()

    def measure_distance(self):
        try:
            # Trigger the sensor
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, False)

            start_time = time.time()
            stop_time = time.time()

            # Capture pulse start
            while GPIO.input(self.echo_pin) == 0:
                start_time = time.time()
                if time.time() - start_time > 0.02:  # Timeout if sensor takes too long
                    return None

            # Capture pulse end
            while GPIO.input(self.echo_pin) == 1:
                stop_time = time.time()
                if stop_time - start_time > 0.02:  # Timeout if sensor takes too long
                    return None

            # Calculate distance (Time * Speed of Sound / 2)
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2  # Distance in cm

            return distance
        except Exception as e:
            logging.warning(f"Error measuring distance: {e}")
            return None

    def get_smoothed_distance(self):
        distance = self.measure_distance()
        if distance is not None:
            self.distance_history.append(distance)
            return np.mean(self.distance_history)  # Moving average smoothing
        return None

    def detect_hand_gesture(self):
        logging.info("Starting hand gesture detection...")
        last_gesture_time = time.time()

        while True:
            current_distance = self.get_smoothed_distance()

            if current_distance is None:
                time.sleep(self.gesture_interval)
                continue

            current_time = time.time()
            if current_time - last_gesture_time < self.debounce_time:
                time.sleep(self.gesture_interval)
                continue

            if self.distance_range[0] <= current_distance <= self.distance_range[1]:
                logging.info("Hand Gesture Detected")
                last_gesture_time = current_time
                # Action: Invoke speech recognition or any other action
                # For example: self.invoke_speech_recognition()
                # Add your action here

            time.sleep(self.gesture_interval)

    def start_hand_gesture_detection(self):
        hand_gesture_thread = threading.Thread(target=self.detect_hand_gesture, daemon=True)
        hand_gesture_thread.start()

    def stop(self):
        logging.info("Stopping gesture detection...")
        self.cleanup_gpio()

# Example usage:
if __name__ == "__main__":
    try:
        gesture_module = GestureModule()
        gesture_module.start_hand_gesture_detection()

        while True:
            time.sleep(0.01)  # Keep the main thread alive with a minimal sleep to reduce CPU load
    except KeyboardInterrupt:
        gesture_module.stop()
        logging.info("Gesture detection stopped.")