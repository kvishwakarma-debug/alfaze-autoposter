import os
import requests
import subprocess

def ensure_music():
    os.makedirs("assets", exist_ok=True)
    path = "assets/sukoon_lofi.mp3"

    if os.path.exists(path) and os.path.getsize(path) > 50000:
        print(f"Using local music: {os.path.getsize(path)} bytes")
        return path

    urls = [
        "https://cdn.pixabay.com/download/audio/2022/10/30/audio_fbd42a7dbd.mp3?filename=lofi-chill-140858.mp3",
    ]

    for url in urls:
        try:
            print(f"Trying: {url}")
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            print(f"Size: {len(r.content)}")
            if len(r.content) > 100000:
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"Music OK: {len(r.content)}")
                return path
        except Exception as e:
            print(f"Fail: {e}")
            continue

    try:
        print("Creating silent fallback audio...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "7", "-q:a", "9", "-acodec", "libmp3lame", path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(path):
            print("Silent audio created")
            return path
    except Exception as e:
        print(f"Silent audio fail: {e}")

    print("No audio, silent reel")
    return None
