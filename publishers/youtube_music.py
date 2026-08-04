import os, json, random
from pathlib import Path

MUSIC_DIR = Path("assets/music")
USED_LOG = MUSIC_DIR / "used_tracks.json"

YT_LINKS = {
    "sad": [
        "https://www.youtube.com/watch?v=77ZpmGTgnrg",
        "https://www.youtube.com/watch?v=1ox7W2rXQ0E",
        "https://www.youtube.com/watch?v=RBumgq5yVrA",
    ],
    "romantic": [
        "https://www.youtube.com/watch?v=9mDzmvH0B4U",
        "https://www.youtube.com/watch?v=DWcJFNfaw9c",
    ],
    "peaceful": [
        "https://www.youtube.com/watch?v=lTRiuFIWV54",
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    ],
    "lofi": [
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    ]
}

def get_mood(text):
    t = text.lower()
    if any(w in t for w in ["dard","gham","barbaad","tanhai","कमी","थकान","ग़म"]):
        return "sad"
    if any(w in t for w in ["ishq","mohabbat","labon","aankhein"]):
        return "romantic"
    return "lofi"

def load_used():
    if USED_LOG.exists():
        try:
            return json.loads(USED_LOG.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_used(lst):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    USED_LOG.write_text(json.dumps(lst, indent=2), encoding="utf-8")

def download_yt(url, out_path):
    try:
        import yt_dlp
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(out_path).replace('.mp3',''),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"YT fail: {e}")
        return False

def create_silent_mp3(path, duration=7):
    # Fallback - agar kuch bhi na mile to silent mp3 banao taaki "No Sound" error na aaye
    try:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(duration), "-q:a", "9", "-acodec", "libmp3lame", str(path)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Silent create fail: {e}")
        return False

def ensure_music_for_shayari(shayari_data):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    for k in YT_LINKS:
        (MUSIC_DIR / k).mkdir(parents=True, exist_ok=True)

    mood = get_mood(shayari_data.get("text",""))
    print(f"MOOD: {mood}")
    used = load_used()
    folder = MUSIC_DIR / mood

    # Try YT download
    urls = YT_LINKS.get(mood, YT_LINKS["lofi"])
    random.shuffle(urls)
    for url in urls:
        fname = f"{mood}_{random.randint(10000,99999)}.mp3"
        out = folder / fname
        print(f"Trying YT: {url}")
        if download_yt(url, out):
            mp3s = sorted(folder.glob("*.mp3"), key=lambda x: x.stat().st_mtime, reverse=True)
            if mp3s:
                chosen = mp3s[0]
                if chosen.stat().st_size > 10000: # Check file is not empty
                    print(f"Got YT music: {chosen}")
                    used.append(chosen.name)
                    save_used(used)
                    return str(chosen)

    # Try any existing local
    all_mp3 = [p for p in MUSIC_DIR.rglob("*.mp3") if p.stat().st_size > 10000]
    if all_mp3:
        chosen = random.choice(all_mp3)
        print(f"Using existing local: {chosen}")
        return str(chosen)

    # LAST FALLBACK - create silent to avoid "No Sound" error
    fallback = MUSIC_DIR / "fallback_silent.mp3"
    if create_silent_mp3(fallback, 7):
        print(f"Created silent fallback: {fallback}")
        return str(fallback)

    return None
