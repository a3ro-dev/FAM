import os
import concurrent.futures
from pytube import YouTube
from moviepy.editor import AudioFileClip
from youtube_search import YoutubeSearch
from fuzzywuzzy import fuzz

class MusicSearch:
    def __init__(self):
        self.output_path = 'F:\\ai-assistant\\pico-files\\music'

    def search_local_music(self, song_name):
        for filename in os.listdir(self.output_path):
            if filename.endswith(".mp3"):
                match_ratio = fuzz.ratio(song_name.lower(), filename.lower())
                if match_ratio > 70:
                    return os.path.join(self.output_path, filename)
        return None

    def search_youtube(self, song_name):
        try:
            results = YoutubeSearch(song_name, max_results=1).to_dict()
            if not results:
                print(f"No results for {song_name}")
                return None
            url = f"https://www.youtube.com{results[0]['url_suffix']}" #type: ignore
            return url
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None

    def download_audio(self, url):
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream is None:
                print(f"No audio streams found for {url}")
                return None
            audio_stream.download(self.output_path)
            return os.path.join(self.output_path, audio_stream.default_filename)
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None

    def convert_to_mp3(self, video_path):
        try:
            audio_path = os.path.join(self.output_path, f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3")
            audio = AudioFileClip(video_path)
            audio.write_audiofile(audio_path)
            os.remove(video_path)
            return audio_path
        except Exception as e:
            print(f"Error converting to MP3: {e}")
            return None

    def search_and_download_music(self, song_name):
        local_file = self.search_local_music(song_name)
        if local_file:
            return local_file

        url = self.search_youtube(song_name)
        if not url:
            return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_download = executor.submit(self.download_audio, url)
            video_path = future_download.result()

        if video_path:
            audio_path = self.convert_to_mp3(video_path)
            return audio_path
        return None