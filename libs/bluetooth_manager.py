import subprocess
import logging

class BluetoothManager:
    """
    A class to manage Bluetooth operations, including starting and stopping Bluetooth mode.
    Attributes:
    -----------
    is_bluetooth_mode_on : bool
        A flag indicating whether Bluetooth mode is currently on.
    Methods:
    --------
    __init__():
        Initializes the BluetoothManager with Bluetooth mode off.
    start_bluetooth_mode():
        Starts Bluetooth mode by initializing PulseAudio, setting Bluetooth agent mode,
        making the device discoverable and pairable, and setting the default audio sink to Bluetooth.
        Logs the status and handles errors if any subprocess calls fail.
    stop_bluetooth_mode():
        Stops Bluetooth mode by unloading Bluetooth modules and stopping PulseAudio.
        Logs the status and handles errors if any subprocess calls fail.
    """
    def __init__(self):
        self.is_bluetooth_mode_on = False

    def start_bluetooth_mode(self):
        if self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already on.")
            return

        try:
            # Start PulseAudio
            subprocess.run(["pulseaudio", "--start"], check=True)
            # Set Bluetooth agent to NoInputNoOutput mode
            subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], check=True)
            # Make the device discoverable
            subprocess.run(["bluetoothctl", "discoverable", "on"], check=True)
            # Make the device pairable
            subprocess.run(["bluetoothctl", "pairable", "on"], check=True)
            # Set the default audio sink to Bluetooth
            subprocess.run(["pactl", "load-module", "module-bluetooth-discover"], check=True)
            subprocess.run(["pactl", "load-module", "module-bluetooth-policy"], check=True)

            self.is_bluetooth_mode_on = True
            logging.info("Bluetooth mode started. The device is now acting as a Bluetooth speaker.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start Bluetooth mode: {e}")

    def stop_bluetooth_mode(self):
        if not self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already off.")
            return

        try:
            # Unload Bluetooth modules
            subprocess.run(["pactl", "unload-module", "module-bluetooth-discover"], check=True)
            subprocess.run(["pactl", "unload-module", "module-bluetooth-policy"], check=True)
            # Stop PulseAudio
            subprocess.run(["pulseaudio", "--kill"], check=True)

            self.is_bluetooth_mode_on = False
            logging.info("Bluetooth mode stopped.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to stop Bluetooth mode: {e}")

# Example usage
if __name__ == "__main__":
    bt_manager = BluetoothManager()
    bt_manager.start_bluetooth_mode()
    input("Press Enter to stop Bluetooth mode...")
    bt_manager.stop_bluetooth_mode()