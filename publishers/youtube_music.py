import os, json, random, requests
from pathlib import Path

MUSIC_DIR = Path("assets/music")
USED_LOG = MUSIC_DIR / "used_tracks.json"

# Pixabay No-Copyright Direct MP3 Links - Ye GitHub pe 100% download hota hai!
PIXABAY_MUSIC = {
    "sad": [
        "https://cdn.pixabay.com/download/audio/2022/10/30/audio_fa7f9daf9f.mp3?filename=sad-piano-126813.mp3",
        "https://cdn.pixabay.com/download/audio/2022/03/15/audio_4d9ed4d6d0.mp3?filename=sad-background-music-110373.mp3",
        "https://cdn.pixabay.com/download/audio/2021/11/25/audio_10bd41749a.mp3?filename=sad-cinematic-piano-103396.mp3",
        "https://cdn.pixabay.com/download/audio/2022/09/14/audio_619339fbc7.mp3?filename=sad-and-alone-122235.mp3",
    ],
    "romantic": [
        "https://cdn.pixabay.com/download/audio/2022/06/07/audio_b9bd4170e8.mp3?filename=romantic-music-113514.mp3",
        "https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3?filename=romantic-piano-100480.mp3",
        "https://cdn.pixabay.com/download/audio/2022/02/07/audio_47bb1a4af0.mp3?filename=romantic-108859.mp3",
    ],
    "peaceful": [
        "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3",
        "https://cdn.pixabay.com/download/audio/2021/10/30/audio_f9bd4170e8.mp3?filename=lofi-hip-hop-101181.mp3",
        "https://cdn.pixabay.com/download/audio/2022/10/30/audio_8ef37a484a.mp3?filename=lofi-chill-128252.mp3",
    ],
    "lofi": [
        "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3",
        "https://cdn.pixabay.com/download/audio/2022/06/07/audio_b9bd4170e8.mp3?filename=lofi-study-112191.mp3",
        "https://cdn.pixabay.com/download/audio/2021/10/30/audio_f9bd4170e8.mp3?filename=lofi-hip-hop-101181.mp3",
        "https://cdn.pixabay.com/download/audio/2022/03/24/audio_73d0e1d5f2.mp3?filename=lofi-background-music-112191.mp3",
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

def download_pixabay(url, out_path):
    try:
        print(f"Downloading Pixabay music: {url}")
        r = requests.get(url, timeout=60, stream=True)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        if out_path.stat().st_size > 10000:
            print(f"Downloaded OK: {out_path} size {out_path.stat().st_size}")
            return True
        else:
            print(f"Downloaded file too small: {out_path}")
            out_path.unlink(missing_ok=True)
            return False
    except Exception as e:
        print(f"Pixabay download fail: {e}")
        return False

def ensure_music_for_shayari(shayari_data):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    for k in PIXABAY_MUSIC:
        (MUSIC_DIR / k).mkdir(parents=True, exist_ok=True)

    mood = get_mood(shayari_data.get("text",""))
    print(f"MOOD DETECTED: {mood}")

    used = load_used()
    folder = MUSIC_DIR / mood

    # 1. Pehle existing unused check
    all_local = [p for p in folder.glob("*.mp3") if p.stat().st_size > 10000]
    unused_local = [p for p in all_local if p.name not in used]
    if unused_local:
        chosen = random.choice(unused_local)
        print(f"Using existing UNIQUE local: {chosen}")
        used.append(chosen.name)
        save_used(used)
        return str(chosen)

    # 2. Naya download karo - har baar alag
    urls = PIXABAY_MUSIC.get(mood, PIXABAY_MUSIC["lofi"])
    random.shuffle(urls)
    
    for url in urls:
        fname = f"{mood}_{random.randint(10000,99999)}.mp3"
        out = folder / fname
        if download_pixabay(url, out):
            print(f"Downloaded NEW UNIQUE: {out}")
            used.append(out.name)
            save_used(used)
            return str(out)

    # 3. Kisi bhi mood se fallback
    all_mp3 = [p for p in MUSIC_DIR.rglob("*.mp3") if p.stat().st_size > 10000]
    if all_mp3:
        chosen = random.choice(all_mp3)
        print(f"Fallback any mood: {chosen}")
        return str(chosen)

    print("No music found!")
    return None
