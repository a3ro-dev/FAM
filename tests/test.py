import os
import openai
import uuid
import re

openai.api_key = 'sk-proj-K8hfsSF9vbG1ccu7Mo50T3BlbkFJXB6nXSORFrhYVjkzTWaR'

# Directory to save the audio files
output_dir = "./tts_audio_files"
os.makedirs(output_dir, exist_ok=True)

# List of texts to convert to speech
texts_to_convert = [
    "Hello! How can I help you today?",
    "I'm doing great! How can I help you today?",
    "Please stop the music player first by saying 'stop music'.",
    "Here are the top news headlines...",
    "Pausing music...",
    "Unpausing music...",
    "Stopping music...",
    "Playing next track...",
    "Quitting the program",
    "Game stopped. Hope you enjoyed!",
    "Seeking forward by 10 seconds",
    "Invalid time. Please provide the number of seconds to seek forward.",
    "Please provide the task!",
    "Please provide the task to search for!",
    "No matching task found.",
]

def sanitize_filename(text):
    # Remove non-alphanumeric characters and replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', text)[:50]  # Limit filename length to 50 characters

def generate_tts_audio(text):
    try:
        # Generate speech using OpenAI TTS
        response = openai.audio.speech.create(
            model='tts-1',
            voice='shimmer',
            input=text,
        )

        # Generate a sanitized filename based on the text
        filename = sanitize_filename(text)
        save_file_path = os.path.join(output_dir, f"{filename}.mp3")

        # Save the audio to a file
        response.stream_to_file(save_file_path)

        print(f"{save_file_path}: A new audio file was saved successfully!")
    except Exception as e:
        print(f"Error in generate_tts_audio: {e}")

# Convert each text in the list to speech and save the audio files
for text in texts_to_convert:
    generate_tts_audio(text)