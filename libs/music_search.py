import os
import concurrent.futures
import argparse
import logging
from pytube import YouTube
from moviepy.editor import AudioFileClip
from youtube_search import YoutubeSearch
from fuzzywuzzy import fuzz
import yaml
from typing import Optional

# Load configuration
with open('conf/config.yaml') as file:
    config = yaml.safe_load(file)

# Constants for configuration keys and file extensions
CONFIG_PATH = 'conf/config.yaml'
MUSIC_EXTENSIONS = ('.mp3',)

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('moviepy').setLevel(logging.CRITICAL)

def load_config(path: str) -> dict:
    with open(path) as file:
        return yaml.safe_load(file)

class MusicSearch:
    """
    A class to search for music locally and on YouTube, download audio, and convert it to MP3 format.
    Methods
    -------
    __init__():
        Initializes the MusicSearch object with configuration and a thread pool executor.
    shutdown():
        Shuts down the thread pool executor.
    search_local_music(song_name: str) -> Optional[str]:
        Searches for a song in the local music directory.
    search_youtube(song_name: str) -> Optional[str]:
        Searches for a song on YouTube and returns the URL of the first result.
    download_audio(url: str) -> Optional[str]:
        Downloads audio from a YouTube URL and saves it to the local music directory.
    convert_to_mp3(video_path: str) -> Optional[str]:
        Converts a downloaded video file to MP3 format and removes the original video file.
    search_and_download_music(song_name: str) -> Optional[str]:
        Searches for a song locally and on YouTube, downloads it, and converts it to MP3 format.
    """
    def __init__(self):
        config = load_config(CONFIG_PATH)
        self.output_path = config['main']['music_path']
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def shutdown(self):
        self.executor.shutdown(wait=True)

    def search_local_music(self, song_name: str) -> Optional[str]:
        for filename in os.listdir(self.output_path):
            if filename.endswith(MUSIC_EXTENSIONS):
                match_ratio = fuzz.ratio(song_name.lower(), filename.lower())
                if match_ratio > 70:
                    return os.path.join(self.output_path, filename)
        return None

    def search_youtube(self, song_name: str) -> Optional[str]:
        try:
            results = YoutubeSearch(song_name, max_results=1).to_dict()
            if not results:
                logging.info(f"No results for {song_name}")
                return None
            return f"https://www.youtube.com{results[0]['url_suffix']}"  # type: ignore
        except Exception as e:
            logging.error(f"Error searching YouTube: {e}")
            return None

    def download_audio(self, url: str) -> Optional[str]:
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream is None:
                logging.info(f"No audio streams found for {url}")
                return None
            audio_stream.download(self.output_path)
            return os.path.join(self.output_path, audio_stream.default_filename)
        except Exception as e:
            logging.error(f"Error downloading audio: {e}")
            return None

    def convert_to_mp3(self, video_path: str) -> Optional[str]:
        try:
            audio_path = os.path.join(self.output_path, f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3")
            audio = AudioFileClip(video_path)
            audio.write_audiofile(audio_path)
            os.remove(video_path)
            return audio_path
        except Exception as e:
            logging.error(f"Error converting to MP3: {e}")
            return None

    def search_and_download_music(self, song_name: str) -> Optional[str]:
        local_file = self.search_local_music(song_name)
        if local_file:
            return local_file

        url = self.search_youtube(song_name)
        if not url:
            return None

        future_download = self.executor.submit(self.download_audio, url)
        video_path = future_download.result()

        if video_path:
            return self.convert_to_mp3(video_path)
        return None

def main():
    parser = argparse.ArgumentParser(description='Search and download a song.')
    parser.add_argument('song_name', type=str, help='The name of the song to search and download.')
    args = parser.parse_args()

    music_search = MusicSearch()
    try:
        path = music_search.search_and_download_music(args.song_name)
        print(path)
    finally:
        music_search.shutdown()

# Example usage
if __name__ == "__main__":
    main()