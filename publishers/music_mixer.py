import os, requests

LOFI_URL = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808c3a07e.mp3?filename=lofi-study-112191.mp3"

def ensure_music():
    os.makedirs("assets", exist_ok=True)
    path = "assets/sukoon_lofi.mp3"
    if not os.path.exists(path):
        print("⬇️ Downloading lofi...")
        r = requests.get(LOFI_URL, timeout=60)
        open(path, "wb").write(r.content)
    return path
