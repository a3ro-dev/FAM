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
            # Start bluetoothctl process
            process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # Send commands to bluetoothctl
            commands = [
                'agent NoInputNoOutput',
                'default-agent',
                'power on',
                'discoverable on',
                'pairable on',
                'agent on',
            ]
            for cmd in commands:
                logging.info(f"Sending command: {cmd}")
                process.stdin.write(cmd + '\n')
                process.stdin.flush()
                time.sleep(0.5)  # Small delay to ensure command execution

            self.is_bluetooth_mode_on = True
            logging.info("Bluetooth mode started. The device is now discoverable and pairable.")

            # Connect to the paired device
            self.connect_paired_device()

            # Play connection sound
            self.play_sound("/home/pi/FAM/assets/audio/success.mp3")
        except Exception as e:
            logging.error(f"Failed to start Bluetooth mode: {e}")

    def stop_bluetooth_mode(self):
        if not self.is_bluetooth_mode_on:
            logging.info("Bluetooth mode is already off.")
            return

        try:
            # Start bluetoothctl process
            process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # Send commands to bluetoothctl
            commands = [
                'discoverable off',
                'pairable off',
                'agent off',
            ]
            for cmd in commands:
                logging.info(f"Sending command: {cmd}")
                process.stdin.write(cmd + '\n')
                process.stdin.flush()
                time.sleep(0.5)

            self.is_bluetooth_mode_on = False
            logging.info("Bluetooth mode stopped.")

            # Play disconnection sound
            self.play_sound("/home/pi/FAM/assets/audio/load.mp3")
        except Exception as e:
            logging.error(f"Failed to stop Bluetooth mode: {e}")

    def connect_paired_device(self):
        try:
            # List paired devices
            result = subprocess.run(['bluetoothctl', 'paired-devices'], capture_output=True, text=True)
            paired_devices = result.stdout.strip().split('\n')

            if paired_devices:
                # Extract the MAC address of the first paired device
                device_info = paired_devices[0].split()
                if len(device_info) >= 2:
                    device_mac = device_info[1]

                    # Start bluetoothctl process
                    process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                    # Trust and connect to the device
                    cmds = [
                        f'trust {device_mac}',
                        f'connect {device_mac}',
                    ]
                    for cmd in cmds:
                        logging.info(f"Sending command: {cmd}")
                        process.stdin.write(cmd + '\n')
                        process.stdin.flush()
                        time.sleep(1)

                    logging.info(f"Connected to paired device: {device_mac}")
                else:
                    logging.warning("No valid paired devices found.")
            else:
                logging.warning("No paired devices found.")
        except Exception as e:
            logging.error(f"Failed to connect to paired device: {e}")

    def play_sound(self, file_path):
        try:
            subprocess.run(['ffplay', '-nodisp', '-autoexit', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    logging.basicConfig(level=logging.INFO)
    bt_manager = BluetoothManager()
    bt_manager.start_bluetooth_mode()
    input("Press Enter to stop Bluetooth mode...")
    bt_manager.stop_bluetooth_mode()