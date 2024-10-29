import yaml
import time
from _fam_assistant import FamAssistant

def load_config():
    with open('conf/config.yaml') as file:
        return yaml.safe_load(file)

def main():
    """
    Main function to initialize and run the FamAssistant.
    This function performs the following steps:
    1. Loads the configuration settings.
    2. Retrieves the access key and music path from the configuration.
    3. Sets the keyword path for the Porcupine listener.
    4. Initializes the FamAssistant with the access key, keyword path, and music path.
    5. Runs the FamAssistant in a separate thread.
    Returns:
        FamAssistant: An instance of the FamAssistant running in a separate thread.
    """
    config = load_config()
    access_key = config['main']['access_key']
    keyword_path = "/home/pi/FAM/model/Hey-Fam_en_raspberry-pi_v3_0_0.ppn"
    music_path = config['main']['music_path']

    porcupine_listener = FamAssistant(access_key=access_key, keyword_path=keyword_path, music_path=music_path)
    porcupine_listener.run_in_thread()

    return porcupine_listener

if __name__ == "__main__":
    porcupine_listener = main()
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        porcupine_listener.stop()
        if porcupine_listener.thread is not None:
            porcupine_listener.thread.join()