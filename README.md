# Fam Assistant

## Overview

Fam Assistant is a versatile, voice and gesture-activated AI assistant designed to run on devices like the Raspberry Pi Zero 2W. It integrates a variety of functionalities such as music playback, task management, Bluetooth control, news updates, and gaming, providing a comprehensive assistant experience tailored for low-end hardware without compromising performance.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
    - [Voice Commands](#voice-commands)
    - [Gesture Controls](#gesture-controls)
5. [Project Structure](#project-structure)
6. [Development](#development)
7. [License](#license)
8. [Support](#support)

---

## Features

### Voice Recognition
- **Wake Word Detection**: Utilizes Porcupine for efficient wake word detection without heavy processing.
- **Command Processing**: Recognizes and processes a wide range of voice commands including music control, task management, Bluetooth operations, and more.
- **GPT Integration**: Handles unknown commands using GPT-powered responses for seamless interactions.

### Gesture Control
- **Hand Gesture Detection**: Uses an ultrasonic sensor to detect hand gestures within a specified distance range (2-5cm).
- **Debounce Mechanism**: Ensures accurate gesture recognition with debounce protection to prevent false triggers.
- **Additional Gestures**: Capable of detecting various gestures like long holds and double taps for enhanced control options.

### Music Management
- **Playback Control**: Play, pause, resume, and stop music effortlessly.
- **Playlist Handling**: Supports shuffle mode and track navigation (next/skip).
- **Volume Control**: Adjusts volume levels during different states of operation.
- **Music Download**: Facilitates downloading of music tracks via voice commands.

### Task Management
- **Add Tasks**: Add new tasks through voice input.
- **Search Tasks**: Search for existing tasks with fuzzy matching for accuracy.

### Bluetooth Integration
- **Bluetooth Mode**: Start and stop Bluetooth mode to act as a Bluetooth speaker.
- **Device Management**: Handles pairing, connecting, and managing Bluetooth devices seamlessly.

### News and Information
- **News Updates**: Fetches and reads out the latest news headlines.
- **Time and Date**: Reports current time and date upon request.

### Gaming Hub
- **Game Launching**: Launch and manage favorite games with voice commands.
- **Email Invitations**: Sends game session invitations with the device's IP address.

### Automation
- **System Control**: Execute system commands like shutdown through voice commands.
- **Chime Notifications**: Plays chimes to indicate successful command detections and operations.

### Utility Functions
- **IP Address Retrieval**: Obtains the device's IP address for network-related functionalities.
- **Graceful Error Handling**: Ensures the assistant remains stable and responsive during unexpected events.

---

## Installation

### Prerequisites
- **Hardware**:
  - Raspberry Pi Zero 2W
  - Ultrasonic Sensor (HC-SR04)
  - Microphone
  - Speakers
  - GPIO Pins: 18 (Trigger), 24 (Echo)
  
- **Software**:
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
    - Fill in the required fields in `config.yaml` with your specific details:
      ```yaml
      main:
        access_key: "YOUR_PORCUPINE_ACCESS_KEY"
        keyword_path: "/path/to/keyword.ppn"
        music_path: "/path/to/music/directory"
        openai_api_key: "YOUR_OPENAI_API_KEY"
        weather_api_key: "YOUR_WEATHER_API_KEY"
        news_api_key: "YOUR_NEWS_API_KEY"
        email:
          sender_email: "akshatsingh14372@outlook.com"
          password: "YOUR_EMAIL_PASSWORD"
          smtp_server: "smtp.example.com"
          smtp_port: 587
      ```

4. **Run the Assistant**:
    ```sh
    python main.py
    ```

---

## Configuration

The configuration file `config.yaml` contains various settings such as API keys, file paths, and other parameters. Ensure all required fields are filled out correctly to enable the assistant's functionalities.

### Configuration Fields

- **access_key**: Your access key for the Porcupine wake word detection engine.
- **keyword_path**: Path to your Porcupine keyword file.
- **music_path**: Path to your music directory.
- **openai_api_key**: Your OpenAI API key for GPT integration.
- **weather_api_key**: Your API key for fetching weather information.
- **news_api_key**: Your API key for fetching news updates.
- **email**:
  - **sender_email**: Your email address used for sending emails.
  - **password**: Your email account password.
  - **smtp_server**: SMTP server address for your email provider.
  - **smtp_port**: SMTP server port (commonly 587 for TLS).

---

## Usage

### Starting the Assistant
- **Launch**: Run the assistant using the command mentioned above. The assistant will start listening for the wake word to activate.

### Voice Commands

#### System Control
- **Shutdown**: "Shutdown"

#### Music Control
- **Play Music**: "Play music"
- **Pause Music**: "Pause music"
- **Resume Music**: "Resume music"
- **Stop Music**: "Stop music"
- **Next Song**: "Next song" or "Skip"
- **Seek Forward**: "Seek forward"

#### Task Management
- **Add Task**: "Add task" or "Add a new task"
- **Search Task**: "Search task"

#### Information
- **Time Inquiry**: "What time is it?" or "What’s the time?" or "Time"
- **Date Inquiry**: "What’s the date?" or "Current date" or "Date"

#### News
- **Get News**: "News"

#### Bluetooth [Not Yet Deployed]
- **Start Bluetooth Mode**: "Start Bluetooth mode", "Enable Bluetooth mode", or "Bluetooth speaker mode"
- **Stop Bluetooth Mode**: "Stop Bluetooth mode", "Disable Bluetooth mode", or "Exit Bluetooth speaker mode"

#### Gaming
- **Play Game**: "Play game" or "Start game"
- **Stop Game**: "Stop game" or "End game"

#### Greetings
- **Greet**: "Hi", "Hello", or "Hey"
- **How Are You**: "How are you?"

#### Automation
- **Start My Day**: "Start my day" or "Good morning"

### Gesture Controls
- **Activate Voice Input**: Hold your hand 2-5cm from the ultrasonic sensor to activate voice input.

---

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

- **Language**: Python 3.x
- **Concurrency**:
  - Utilizes `ThreadPoolExecutor` for handling I/O-bound tasks like command processing and gesture detection.
  - Employs `ProcessPoolExecutor` to leverage all four cores of the Raspberry Pi Zero 2W for CPU-bound operations, ensuring efficient performance and avoiding deadlocks.
  
- **Logging**: Implements structured logging for monitoring and debugging purposes.
- **GPIO Management**: Manages GPIO pins for ultrasonic sensor-based gesture detection with proper setup and cleanup to prevent hardware issues.
- **Error Handling**: Incorporates comprehensive error handling to maintain assistant stability and reliability.
  
### Key Improvements for Multi-Core Utilization
- **ThreadPoolExecutor and ProcessPoolExecutor**:
  - Added `ThreadPoolExecutor` for I/O-bound tasks.
  - Added `ProcessPoolExecutor` for CPU-bound tasks to utilize all four cores effectively.
  
- **Gesture Detection**:
  - Runs gesture detection in a separate thread to prevent blocking the main process.
  
- **Command Processing**:
  - Handles command processing concurrently using executors to distribute the workload across multiple cores.
  
- **Avoiding Deadlocks**:
  - Ensures thread-safe operations with proper locking mechanisms.
  - Separates I/O and CPU-bound tasks to different executors to prevent resource contention.

### Concurrency Model

Fam Assistant employs a hybrid concurrency model to maximize CPU utilization and maintain responsiveness:

1. **ThreadPoolExecutor**: 
   - Handles I/O-bound tasks such as reading audio streams, gesture detection, and command processing.
   - Ensures that blocking operations do not hinder the main execution flow.

2. **ProcessPoolExecutor**:
   - Manages CPU-bound tasks like speech recognition and GPT-powered command handling.
   - Distributes these tasks across multiple CPU cores to enhance performance.

### Performance Optimization

- **Efficient Resource Management**: Proper initialization and cleanup of hardware resources to prevent memory leaks and hardware conflicts.
- **Load Balancing**: Distributes tasks evenly across threads and processes to avoid overloading any single core.
- **Debounce Mechanism**: Minimizes redundant processing by implementing debounce timers for gesture detection.

### Testing and Monitoring

- **Unit Testing**: Implement comprehensive unit tests for each module to ensure individual components function correctly.
- **Performance Monitoring**: Regularly monitor CPU and memory usage to identify and address performance bottlenecks.
- **Logging**: Utilize detailed logging to track application behavior and facilitate debugging.

---

## License

Closed Source
---

## Support

For any questions or issues, reach out at [akshatsingh14372@outlook.com](mailto:akshatsingh14372@outlook.com).

Developer: [a3ro-dev](https://github.com/a3ro-dev)
