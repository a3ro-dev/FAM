import subprocess
import logging
import time

class BluetoothManager:
    """
    Manages Bluetooth operations, including starting and stopping Bluetooth mode.
    """
    def __init__(self):
        self.is_bluetooth_mode_on = False

    def start_bluetooth_mode(self):
        if self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already on.")
            return

        # Ensure Bluetooth service is active
        self.ensure_bluetooth_service_active()

        try:
            # Set Bluetooth agent to NoInputNoOutput mode
            subprocess.run(["bluetoothctl", "agent", "NoInputNoOutput"], check=True)
            # Register the agent
            subprocess.run(["bluetoothctl", "agent", "on"], check=True)
            
            # Retry setting the default agent up to 3 times if it fails
            for attempt in range(3):
                result = subprocess.run(["bluetoothctl", "default-agent"], check=False)
                if result.returncode == 0:
                    logging.info("Default agent successfully set.")
                    break
                logging.warning(f"Attempt {attempt + 1} to set default agent failed.")
                time.sleep(2)
            else:
                logging.error("Failed to set default agent after multiple attempts.")
                return  # Stop further setup if agent setup fails

            # Make the device discoverable and pairable
            subprocess.run(["bluetoothctl", "discoverable", "on"], check=True)
            subprocess.run(["bluetoothctl", "pairable", "on"], check=True)

            self.is_bluetooth_mode_on = True
            logging.info("Bluetooth mode started. The device is now discoverable and pairable.")
            
            # Connect to the paired device
            self.connect_paired_device()
            
            # Play connection sound
            self.play_sound("/home/pi/FAM/assets/audio/success.mp3")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start Bluetooth mode: {e}")

    def stop_bluetooth_mode(self):
        if not self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already off.")
            return

        try:
            # Make the device non-discoverable and non-pairable
            subprocess.run(["bluetoothctl", "discoverable", "off"], check=True)
            subprocess.run(["bluetoothctl", "pairable", "off"], check=True)

            self.is_bluetooth_mode_on = False
            logging.info("Bluetooth mode stopped.")
            
            # Play disconnection sound
            self.play_sound("/home/pi/FAM/assets/audio/load.mp3")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to stop Bluetooth mode: {e}")

    def connect_paired_device(self):
        try:
            # List paired devices
            result = subprocess.run(["bluetoothctl", "paired-devices"], capture_output=True, text=True, check=True)
            paired_devices = result.stdout.splitlines()
            
            if paired_devices:
                # Extract the MAC address of the first paired device
                device_mac = paired_devices[0].split()[1]
                
                # Trust the device
                subprocess.run(["bluetoothctl", "trust", device_mac], check=True)
                
                # Attempt to connect to the device
                connect_attempts = 3
                for attempt in range(connect_attempts):
                    try:
                        subprocess.run(["bluetoothctl", "connect", device_mac], check=True)
                        logging.info(f"Connected to paired device: {device_mac}")
                        break
                    except subprocess.CalledProcessError as e:
                        logging.error(f"Connection attempt {attempt + 1} failed: {e}")
                        if attempt == connect_attempts - 1:
                            logging.error("All connection attempts failed.")
            else:
                logging.warning("No paired devices found.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to connect to paired device: {e}")

    def play_sound(self, file_path):
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to play sound: {e}")

    def ensure_bluetooth_service_active(self):
        try:
            # Start Bluetooth service if it's not already active
            subprocess.run(["sudo", "systemctl", "start", "bluetooth"], check=True)
            logging.info("Bluetooth service is active.")
        except subprocess.CalledProcessError:
            logging.error("Bluetooth service could not be started. Please check your Bluetooth setup.")

# Example usage
if __name__ == "__main__":
    bt_manager = BluetoothManager()
    bt_manager.start_bluetooth_mode()
    input("Press Enter to stop Bluetooth mode...")
    bt_manager.stop_bluetooth_mode()
