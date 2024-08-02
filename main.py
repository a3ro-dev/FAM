import yaml
from _fam_assistant import FamAssistant

def load_config():
    with open('conf/config.yaml') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()
    access_key = config['main']['access_key']
    keyword_path = "/home/pi/FAM/model/wake-mode/Hey-Fam_en_raspberry-pi_v3_0_0.ppn"
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