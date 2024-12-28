import yaml
import time
import threading
import subprocess
from pathlib import Path
from multiprocessing import Process
from _fam_assistant import FamAssistant

def load_config():
    with open('conf/secrets.yaml') as file:
        return yaml.safe_load(file)

def start_streamlit_app(script_path):
    """Launch a Streamlit application."""
    subprocess.run(['streamlit', 'run', script_path])

def start_streamlit_apps():
    """Start all Streamlit apps in the pages directory."""
    pages_dir = Path(__file__).parent / 'pages'
    streamlit_files = [
        pages_dir / 'versionManagement.py',
        pages_dir / 'secretsEditor.py',
        pages_dir / 'musicManagement.py'
    ]
    
    processes = []
    for file in streamlit_files:
        if file.exists():
            p = Process(target=start_streamlit_app, args=(str(file),))
            p.start()
            processes.append(p)
    return processes

def main():
    """
    Main function to initialize and run the FamAssistant.
    This function performs the following steps:
    1. Loads the configuration settings.
    2. Retrieves the access key and music path from the configuration.
    3. Sets the keyword path for the Porcupine listener.
    4. Initializes the FamAssistant with the access key, keyword path, and music path.
    5. Runs the FamAssistant in a separate thread.
    6. Starts Streamlit apps in separate processes.
    Returns:
        FamAssistant: An instance of the FamAssistant running in a separate thread.
        list: A list of processes running the Streamlit apps.
    """
    config = load_config()
    access_key = config['main']['access_key']
    keyword_path = "/home/pi/FAM/model/Hey-Fam_en_raspberry-pi_v3_0_0.ppn"
    music_path = config['main']['music_path']

    assistant = FamAssistant(access_key=access_key, keyword_path=keyword_path, music_path=music_path)

    # Start the assistant in a separate thread
    assistant_thread = threading.Thread(target=assistant.start, daemon=True)
    assistant_thread.start()

    # Start Streamlit apps
    streamlit_processes = start_streamlit_apps()

    return assistant, assistant_thread, streamlit_processes

if __name__ == "__main__":
    assistant, assistant_thread, streamlit_processes = main()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        assistant.stop()
        assistant_thread.join()
        # Terminate Streamlit processes
        for p in streamlit_processes:
            p.terminate()
            p.join()