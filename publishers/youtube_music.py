import os, json, random
from pathlib import Path

MUSIC_DIR = Path("assets/music")
USED_LOG = MUSIC_DIR / "used_tracks.json"

YT_LINKS = {
    "sad": [
        "https://www.youtube.com/watch?v=77ZpmGTgnrg",
        "https://www.youtube.com/watch?v=1ox7W2rXQ0E",
        "https://www.youtube.com/watch?v=RBumgq5yVrA",
        "https://www.youtube.com/watch?v=2b9aB4sM6xQ",
    ],
    "romantic": [
        "https://www.youtube.com/watch?v=9mDzmvH0B4U",
        "https://www.youtube.com/watch?v=5qap5aO4i9A",
        "https://www.youtube.com/watch?v=DWcJFNfaw9c",
    ],
    "peaceful": [
        "https://www.youtube.com/watch?v=lTRiuFIWV54",
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    ],
    "lofi": [
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
        "https://www.youtube.com/watch?v=77ZpmGTgnrg",
    ]
}

def get_mood(text):
    t = text.lower()
    if any(w in t for w in ["dard","gham","barbaad","tanhai","कमी","थकान","ग़म"]):
        return "sad"
    if any(w in t for w in ["ishq","mohabbat","labon","aankhein"]):
        return "romantic"
    if any(w in t for w in ["sukoon","dua","सुकून"]):
        return "peaceful"
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
        print(f"YT fail {e}")
        return False

def ensure_music_for_shayari(shayari_data):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    for k in YT_LINKS:
        (MUSIC_DIR / k).mkdir(parents=True, exist_ok=True)
    mood = get_mood(shayari_data.get("text",""))
    print(f"MOOD: {mood}")
    used = load_used()
    folder = MUSIC_DIR / mood
    urls = YT_LINKS.get(mood, YT_LINKS["lofi"])
    random.shuffle(urls)
    for url in urls:
        fname = f"{mood}_{random.randint(10000,99999)}.mp3"
        out = folder / fname
        print(f"Downloading YT: {url} -> {fname}")
        if download_yt(url, out):
            mp3s = sorted(folder.glob("*.mp3"), key=lambda x: x.stat().st_mtime, reverse=True)
            if mp3s:
                chosen = mp3s[0]
                print(f"Downloaded: {chosen}")
                used.append(chosen.name)
                save_used(used)
                return str(chosen)
    all_mp3 = list(MUSIC_DIR.rglob("*.mp3"))
    if all_mp3:
        chosen = random.choice(all_mp3)
        print(f"Fallback: {chosen}")
        return str(chosen)
    return None
