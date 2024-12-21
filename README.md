# Fam Assistant

A voice and gesture-controlled AI assistant optimized for Raspberry Pi Zero 2W. It provides music playback, task management, game hosting, and GPT-powered conversations.

## Features

### Core Functions
- Voice control with GPT integration
- Gesture control using ultrasonic sensor
- Music playback and playlist management 
- Task/reminder system
- Game server hosting
- Raspotify (Spotify Connect) control

### Technical Details
- Multi-threaded architecture for responsive operation
- GPIO-based gesture detection (HC-SR04 sensor)
- Audio playback via pygame
- Local music library with Spotify sync
- HTTP game server with email invites

## Setup

1. Clone and install:
```bash
git clone https://github.com/a3ro-dev/FAM
cd FAM
pip install -r requirements.txt
```

2. Configure `conf/config.yaml`:
```yaml
main:
    access_key: "<your_access_key_here>"
    keyword_path: "<your_keyword_path_here>"
    music_path: "<your_music_path_here>"
    groq_api_key: "<your_groq_api_key_here>"
    openai_api_key: "<your_openai_api_key_here>"
    model_name: "<your_model_name_here>"
utilities:
    author: "<your_name_here>"
    audio_files:
        success: "<path_to_success_audio_file_here>"
        error: "<path_to_error_audio_file_here>"
        load: "<path_to_load_audio_file_here>"
    model_path: "<path_to_model_here>"
    weather_api_key: "<your_weather_api_key_here>"
    news_api_key: "<your_news_api_key_here>"
    email:
        sender_email: "<your_email_here>"
        sender_password: "<your_password_here>"
        smtp_server: "<your_smtp_server_here>"
        smtp_port: "<your_smtp_port_here>"
    image_path: "<path_to_image_here>"
music_search:
    output_path: "<path_to_output_here>"
```
3. Run:
```bash
python main.py
```

## Usage

### Voice Commands

#### System
- "Shutdown" - Power off system
- "Start my day" - Morning routine
- "Enable/disable raspotify" - Control Spotify Connect

#### Media
- "Play/pause/resume/stop music"
- "Play [song name]"
- "Next/skip" - Next track
- "Download [song]" - Add to library

#### Games
- "Play/start game" - Launch game server
- "Stop/end game" - Stop server

#### Tasks
- "Add task" - Create new task
- "Search task" - Find existing task

### Gesture Control
Hold hand 2-5cm from ultrasonic sensor to activate voice input.

## Project Structure
```
FamAssistant/
├── 

main.py
_fam_assistant.py

                      # Main assistant implementation
├── libs/
│   ├── bluetooth_manager.py     # Bluetooth functionality
│   ├── clock.py                 # Time and task management
│   ├── games.py                 # Games management
│   ├── gpt.py                   # GPT integration
│   ├── music.py                 # Music player implementation
│   ├── music_search.py          # Music search and download
│   └── utilities.py             # Utility functions
├── assets/
│   └── tts_audio_files/         # Text-to-speech audio files
├── conf/
│   ├── config.example.yaml      # Example configuration file
│   └── config.yaml              # User configuration file
├── 

README.md

                    # Project documentation
└── 

requirements.txt

             # Python dependencies
```

---

## Development

- Built with Python 3.11.x
- Uses ThreadPoolExecutor for I/O operations
- Implements hardware debouncing for gesture detection
- Comprehensive error handling and logging

## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nc-nd/4.0/).

---

## Support

For any questions or issues, reach out at [akshatsingh14372@outlook.com](mailto:akshatsingh14372@outlook.com).

Developer: [a3ro-dev](https://github.com/a3ro-dev)
