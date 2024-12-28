import os
import concurrent.futures
import argparse
import logging
from pytube import YouTube
from moviepy.editor import AudioFileClip
from youtube_search import YoutubeSearch
from fuzzywuzzy import fuzz
import yaml
from typing import Optional, Set
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Load configuration
with open('conf/secrets.yaml') as file:
    config = yaml.safe_load(file)

# Constants for configuration keys and file extensions
CONFIG_PATH = 'conf/secrets.yaml'
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
        
        # Initialize Spotify client with config values
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=config['spotify']['client_id'],
            client_secret=config['spotify']['client_secret']
        ))
        
        self.rate_limit_window = 60  # 60 seconds window
        self.max_requests = 100      # max 100 requests per window
        self.request_timestamps: list = []

    def _check_rate_limit(self):
        """Implements rate limiting for API requests"""
        current_time = time.time()
        # Remove timestamps older than the window
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if current_time - ts < self.rate_limit_window]
        
        if len(self.request_timestamps) >= self.max_requests:
            sleep_time = self.request_timestamps[0] + self.rate_limit_window - current_time
            if sleep_time > 0:
                logging.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.request_timestamps.append(current_time)

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
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                yt = YouTube(url)
                audio_stream = yt.streams.filter(only_audio=True).first()
                if audio_stream is None:
                    logging.info(f"No audio streams found for {url}")
                    return None
                audio_stream.download(self.output_path)
                return os.path.join(self.output_path, audio_stream.default_filename)
            except Exception as e:
                logging.error(f"Error downloading audio (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error("Max retries reached, download failed")
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

    def get_playlist_tracks(self, playlist_url):
        """Get all tracks from a Spotify playlist."""
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        results = self.sp.playlist_tracks(playlist_id)
        tracks = []
        
        while results:
            for item in results['items']:
                track = item['track']
                track_name = f"{track['name']} - {', '.join([artist['name'] for artist in track['artists']])}"
                tracks.append(track_name)
            
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
                
        return tracks

    def sync_playlist(self, playlist_url):
        """Sync local music directory with Spotify playlist with rate limiting and error handling."""
        try:
            # Get current playlist tracks
            self._check_rate_limit()
            playlist_tracks = set(self.get_playlist_tracks(playlist_url))
            
            if not playlist_tracks:
                logging.error("No tracks found in playlist or failed to fetch playlist")
                return

            # Get current local files
            try:
                local_files = {os.path.splitext(f)[0] for f in os.listdir(self.output_path) 
                             if f.endswith(MUSIC_EXTENSIONS)}
            except OSError as e:
                logging.error(f"Failed to read music directory: {e}")
                return

            tracks_to_add = playlist_tracks - local_files
            tracks_to_remove = local_files - playlist_tracks

            # Remove tracks not in playlist
            for track in tracks_to_remove:
                try:
                    for ext in MUSIC_EXTENSIONS:
                        file_path = os.path.join(self.output_path, f"{track}{ext}")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logging.info(f"Removed: {track}")
                except OSError as e:
                    logging.error(f"Failed to remove {track}: {e}")

            # Download new tracks with delay and rate limiting
            for track in tracks_to_add:
                try:
                    logging.info(f"Downloading: {track}")
                    self._check_rate_limit()
                    self.search_and_download_music(track)
                    time.sleep(2)  # 2-second delay between downloads
                except Exception as e:
                    logging.error(f"Failed to download {track}: {e}")
                    continue

        except Exception as e:
            logging.error(f"Playlist sync failed: {e}")

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