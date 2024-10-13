# Fam Assistant

## Overview

Fam Assistant is a voice-activated assistant designed to run on devices like the Raspberry Pi. It integrates various functionalities such as music playback, task management, and game launching, providing a comprehensive assistant experience.

## Features

- **Voice Recognition**: Uses Google Speech Recognition to process voice commands.
- **Music Player**: Play, pause, resume, and stop music.
- **Task Management**: Add and search for tasks.
- **Games Hub**: Launch and manage games.
- **News and Weather**: Fetch and read out the latest news and weather updates.
- **Automation**: Automate tasks like sending emails and downloading content.

## Installation

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Steps

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/a3ro-dev/FAM
    cd FAM
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configuration**:
    - Copy the example configuration file:
      ```sh
      cp conf/config.example.yaml conf/config.yaml
      ```
    - Fill in the required fields in 

config.yaml

 with your specific details:
      - `access_key`: Your access key for the wake word detection engine.
      - `keyword_path`: Path to your keyword file.
      - `music_path`: Path to your music directory.
      - `openai_api_key`: Your OpenAI API key.
      - `weather_api_key`: Your weather API key.
      - `news_api_key`: Your news API key.
      - `email`: Your email configuration (sender email, password, SMTP server, and port).

4. **Run the Assistant**:
    ```sh
    python main.py
    ```

## Usage

### Starting the Assistant

- Run the assistant using the command mentioned above. The assistant will start listening for the wake word.

### Voice Commands

- **Music Commands**:
  - "Play music"
  - "Pause music"
  - "Resume music"
  - "Stop music"
  - "Next song"
  - "Seek forward"

- **Task Management**:
  - "Add task"
  - "Search task"

- **General Commands**:
  - "What's the weather?"
  - "What's the news?"
  - "What's the time?"
  - "What's the date?"

- **Games**:
  - "Play game"
  - "Stop game"

### Configuration

The configuration file 

config.yaml

 contains various settings such as API keys, file paths, and other parameters. Ensure all required fields are filled out correctly.

### Dependencies

- **Audio Processing**:
  - PyAudio
  - pvporcupine
  - pydub

- **Speech Recognition**:
  - SpeechRecognition
  - gTTS

- **Natural Language Processing**:
  - openai
  - wikipedia-api

- **Media Handling**:
  - pygame
  - pytube
  - moviepy

- **Utilities**:
  - fuzzywuzzy
  - pyyaml
  - numpy

### File Structure

- **Main File**:
  - 

_fam_assistant.py

: Main file for the assistant.

- **Libraries**:
  - 

libs

: Contains utility libraries for various functionalities.

- **Static Files**:
  - 

misc

: Contains static files and additional resources.

- **Configuration**:
  - 

conf

: Configuration files.

- **Dependencies**:
  - 

requirements.txt

: List of dependencies.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

### Acknowledgements

- **Google Speech Recognition**: For speech-to-text capabilities.
- **OpenAI**: For natural language processing.
- **Various open-source libraries and tools**: Used in this project.

### Contact

For any questions or issues, please contact [akshatsingh14372@outlook.com].