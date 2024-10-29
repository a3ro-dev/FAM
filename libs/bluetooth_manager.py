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
        Starts Bluetooth mode by setting Bluetooth agent mode,
        making the device discoverable and pairable.
        Logs the status and handles errors if any subprocess calls fail.
    stop_bluetooth_mode():
        Stops Bluetooth mode by making the device non-discoverable and non-pairable.
        Logs the status and handles errors if any subprocess calls fail.
    """
    def __init__(self):
        self.is_bluetooth_mode_on = False

    def start_bluetooth_mode(self):
        if self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already on.")
            return

        try:
            # Set Bluetooth agent to NoInputNoOutput mode
            subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], check=True)
            # Make the device discoverable
            subprocess.run(["bluetoothctl", "discoverable", "on"], check=True)
            # Make the device pairable
            subprocess.run(["bluetoothctl", "pairable", "on"], check=True)

            self.is_bluetooth_mode_on = True
            logging.info("Bluetooth mode started. The device is now discoverable and pairable.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start Bluetooth mode: {e}")

    def stop_bluetooth_mode(self):
        if not self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already off.")
            return

        try:
            # Make the device non-discoverable
            subprocess.run(["bluetoothctl", "discoverable", "off"], check=True)
            # Make the device non-pairable
            subprocess.run(["bluetoothctl", "pairable", "off"], check=True)

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