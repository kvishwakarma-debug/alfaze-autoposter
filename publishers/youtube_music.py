import os, json, random, glob
from pathlib import Path

MUSIC_DIR = Path("assets/music")
USED_LOG = MUSIC_DIR / "used_tracks.json"

# Mood wise YouTube No-Copyright Lofi links (ye saare No-Copyright wale hain)
ROYALTY_FREE_SOURCES = {
    "sad": [
        "https://www.youtube.com/watch?v=77ZpmGTgnrg",
        "https://www.youtube.com/watch?v=2b9aB4sM6xQ",
        "https://www.youtube.com/watch?v=Q5i4tR8u6yI",
        "https://www.youtube.com/watch?v=1ox7W2rXQ0E",
        "https://www.youtube.com/watch?v=RBumgq5yVrA",
    ],
    "romantic": [
        "https://www.youtube.com/watch?v=9mDzmvH0B4U",
        "https://www.youtube.com/watch?v=5qap5aO4i9A",
        "https://www.youtube.com/watch?v=DWcJFNfaw9c",
    ],
    "peaceful": [
        "https://www.youtube.com/watch?v=lTRiuFIWV54",
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
        "https://www.youtube.com/watch?v=5yx6BWlEVcY",
    ],
    "longing": [
        "https://www.youtube.com/watch?v=4xDzrJKXOoY",
        "https://www.youtube.com/watch?v=2F6B9E1a2tQ",
    ],
    "lofi": [
        "https://www.youtube.com/watch?v=jfKfPfyJRdk",
        "https://www.youtube.com/watch?v=5qap5aO4i9A",
        "https://www.youtube.com/watch?v=DWcJFNfaw9c",
    ]
}

def get_mood_from_shayari(text):
    text = text.lower()
    if any(w in text for w in ["dard", "gham", "barbaad", "tanhai", "rula", "mar", "कमी", "थकान", "ग़म"]):
        return "sad"
    if any(w in text for w in ["ishq", "mohabbat", "labon", "aankhein", "इश्क़"]):
        return "romantic"
    if any(w in text for w in ["sukoon", "dua", "khili", "सुकून"]):
        return "peaceful"
    if any(w in text for w in ["intezaar", "इंतज़ार"]):
        return "longing"
    return "lofi"

def load_used_log():
    if USED_LOG.exists():
        try:
            with open(USED_LOG, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_used_log(used_list):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    with open(USED_LOG, "w") as f:
        json.dump(used_list, f, indent=2)

def download_youtube_audio(url, output_path):
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path).replace('.mp3',''),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Download fail: {e}")
        return False

def ensure_music_for_shayari(shayari_data):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    for mood in ROYALTY_FREE_SOURCES.keys():
        (MUSIC_DIR / mood).mkdir(parents=True, exist_ok=True)

    mood = get_mood_from_shayari(shayari_data.get("text",""))
    print(f"Shayari Mood: {mood}")

    used = load_used_log()
    folder = MUSIC_DIR / mood
    all_files = list(folder.glob("*.mp3"))
    # Unused me se chuno - har baar alag gaana
    unused = [f for f in all_files if f.name not in used]

    if unused:
        chosen = random.choice(unused)
        print(f"Using UNIQUE local track: {chosen.name}")
        used.append(chosen.name)
        save_used_log(used)
        return str(chosen)

    # Agar saare use ho gaye ya folder khali hai to naya download karo
    print(f"No unused {mood} track, fetching new from YouTube...")
    urls = ROYALTY_FREE_SOURCES.get(mood, ROYALTY_FREE_SOURCES["lofi"])
    # Aisa URL chuno jo pehle download nahi hua
    random.shuffle(urls)
    for url in urls:
        out_path = folder / f"{mood}_{random.randint(10000,99999)}.mp3"
        if download_youtube_audio(url, out_path):
            # Download hua file dhoondo
            new_files = list(folder.glob("*.mp3"))
            new_files = [f for f in new_files if f.name not in used]
            if new_files:
                chosen = new_files[-1]
                used.append(chosen.name)
                save_used_log(used)
                print(f"Downloaded NEW unique track: {chosen.name}")
                return str(chosen)

    # Last fallback
    all_music = list(MUSIC_DIR.rglob("*.mp3"))
    unused_all = [f for f in all_music if f.name not in used]
    if unused_all:
        chosen = random.choice(unused_all)
        used.append(chosen.name)
        save_used_log(used)
        return str(chosen)

    # Sab use ho gaya to log reset karke phir se
    if all_music:
        print("All tracks used, resetting log for new cycle")
        save_used_log([])
        chosen = random.choice(all_music)
        save_used_log([chosen.name])
        return str(chosen)

    # Koi music hi nahi hai to purana wala
    from.music_mixer import ensure_music
    return ensure_music()
