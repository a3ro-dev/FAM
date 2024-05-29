from pytube import YouTube
from moviepy.editor import AudioFileClip
from youtube_search import YoutubeSearch
from fuzzywuzzy import fuzz

class MusicSearch:
    def search_and_download_music(self, song_name, output_path: str ='F:\\ai-assistant\\pico-files\\music'):
        # Check if the song is already in the output directory
        import os
        for filename in os.listdir(output_path):
            if filename.endswith(".mp3"):
                # Compare the song name with the filename using fuzzy matching
                match_ratio = fuzz.ratio(song_name.lower(), filename.lower())
            if match_ratio > 70:
                return os.path.join(output_path, filename)

        # If the song is not in the output directory, search for it on YouTube
        results = YoutubeSearch(song_name, max_results=1).to_dict()
        if not results:
            print(f"No results for {song_name}")
            return

        # Get the URL of the first video from the search results
        url = f"https://www.youtube.com{results[0]['url_suffix']}" #type: ignore

        # Download the video
        yt = YouTube(url)
        video = yt.streams.first()
        if video is None:
            print(f"No streams found for {url}")
            return

        video.download(output_path)

        # Define paths
        video_path = os.path.join(output_path, video.default_filename)
        audio_path = os.path.join(output_path, f"{video.default_filename.rsplit('.', 1)[0]}.mp3")

        # Extract audio using moviepy
        audio = AudioFileClip(video_path)
        audio.write_audiofile(audio_path)

        # Remove the video file
        os.remove(video_path)

        return audio_path
    
music_search = MusicSearch()
song_path = music_search.search_and_download_music('divine failure')
print(song_path)