import RPi.GPIO as GPIO
import time
import threading
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KalmanFilter:
    def __init__(self, process_variance=1.0, measurement_variance=1.0, initial_estimate=0.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = initial_estimate
        self.error_estimate = 1.0

    def update(self, measurement):
        # Predict step
        prior_estimate = self.estimate
        prior_error = self.error_estimate + self.process_variance

        # Update step
        blending_factor = prior_error / (prior_error + self.measurement_variance)
        self.estimate = prior_estimate + blending_factor * (measurement - prior_estimate)
        self.error_estimate = (1 - blending_factor) * prior_error

        return self.estimate

class GestureModule:
    def __init__(self, trigger_pin=18, echo_pin=24, distance_thresholds=(10, 20), gesture_interval=0.5):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.distance_thresholds = distance_thresholds
        self.gesture_interval = gesture_interval
        self.kalman_filter = KalmanFilter()
        self.previous_distance = None
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

            # Capture pulse end
            while GPIO.input(self.echo_pin) == 1:
                stop_time = time.time()

            # Calculate distance (Time * Speed of Sound / 2)
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2  # Distance in cm

            return self.kalman_filter.update(distance)
        except Exception as e:
            logging.warning(f"Error measuring distance: {e}")
            return None

    def detect_gestures(self):
        self.previous_distance = self.measure_distance()

        while True:
            current_distance = self.measure_distance()

            if current_distance is None:
                time.sleep(self.gesture_interval)
                continue

            if current_distance < self.distance_thresholds[0]:
                logging.info("Hand Wave Detected")
                # Action: Toggle play/pause for music
            elif self.distance_thresholds[0] <= current_distance < self.distance_thresholds[1]:
                logging.info("Hand Hold Detected")
                # Action: Start or stop a timer
            elif current_distance - self.previous_distance > 10:
                logging.info("Hand Swipe Detected (Forward)")
                # Action: Skip to the next song
            elif self.previous_distance - current_distance > 10:
                logging.info("Hand Swipe Detected (Backward)")
                # Action: Skip to the previous song
            elif current_distance < self.previous_distance:
                logging.info("Hand Approach Detected")
                # Action: Increase volume
            elif current_distance > self.previous_distance:
                logging.info("Hand Retreat Detected")
                # Action: Decrease volume

            self.previous_distance = current_distance
            time.sleep(self.gesture_interval)

    def start_gesture_detection(self):
        logging.info("Starting gesture detection...")
        gesture_thread = threading.Thread(target=self.detect_gestures, daemon=True)
        gesture_thread.start()

    def detect_hand_gesture(self):
        logging.info("Starting hand gesture detection...")
        while True:
            current_distance = self.measure_distance()
            if current_distance is not None and 5 <= current_distance <= 10:  # Adjustable range
                logging.info("Hand Gesture Detected")
                return True
            time.sleep(self.gesture_interval)
        return False

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
        gesture_module.start_gesture_detection()
        gesture_module.start_hand_gesture_detection()

        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        gesture_module.stop()
        logging.info("Gesture detection stopped.")
