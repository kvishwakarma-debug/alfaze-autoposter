import os
import requests

def ensure_music():
    os.makedirs("assets", exist_ok=True)
    path = "assets/sukoon_lofi.mp3"

    # Already exists and valid?
    if os.path.exists(path) and os.path.getsize(path) > 50000:
        return path

    urls = [
        "https://cdn.pixabay.com/download/audio/2022/10/30/audio_fbd42a7dbd.mp3?filename=lofi-chill-140858.mp3",
        "https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3?filename=lofi-study-112191.mp3",
    ]

    for url in urls:
        try:
            print(f"Trying: {url}")
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            if len(r.content) > 50000:
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"✅ Music OK: {len(r.content)} bytes")
                return path
        except Exception as e:
            print(f"Fail: {e}")
            continue

    print("⚠️ Music download failed, reel will be silent")
    return None
