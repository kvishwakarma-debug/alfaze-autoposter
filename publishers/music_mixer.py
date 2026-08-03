import os, requests
from moviepy.editor import VideoFileClip, AudioFileClip

# Copyright-free Lofi (Pixabay - No Copyright)
LOFI_URL = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808c3a07e.mp3?filename=lofi-study-112191.mp3"

def ensure_music():
    os.makedirs("assets", exist_ok=True)
    path = "assets/sukoon_lofi.mp3"
    if not os.path.exists(path):
        print("⬇️ Downloading lofi music...")
        r = requests.get(LOFI_URL)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

def add_music_to_video(video_path, output_path="final_reel.mp4"):
    music_path = ensure_music()
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(music_path).subclip(0, video.duration).volumex(0.30)
        final = video.set_audio(audio)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        print(f"✅ Music mixed: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Music mix failed, using original: {e}")
        return video_path
