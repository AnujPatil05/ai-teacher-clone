import yt_dlp
import os

def download_videos(playlist_url, max_videos=6):
    """Download first N videos from playlist"""
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'playlistend': max_videos,  # Only first 6 videos
        'quiet': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading {max_videos} videos...")
        ydl.download([playlist_url])
    
    print("✓ Videos downloaded successfully!")

if __name__ == "__main__":
    playlist = "https://www.youtube.com/playlist?list=PLxCzCOWd7aiEszeDTf1kW3uF-Yy-MFjw8"
    download_videos(playlist, max_videos=6)