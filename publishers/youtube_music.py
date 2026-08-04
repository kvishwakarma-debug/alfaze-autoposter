import os, json, random, requests
from pathlib import Path

MUSIC_DIR = Path("assets/music/sad")
USED_LOG = Path("assets/music/used_tracks.json")

SAD_MUSIC = [
    "https://cdn.pixabay.com/download/audio/2022/10/30/audio_fa7f9daf9f.mp3?filename=sad-piano-126813.mp3",
    "https://cdn.pixabay.com/download/audio/2022/03/15/audio_4d9ed4d6d0.mp3?filename=sad-background-music-110373.mp3",
    "https://cdn.pixabay.com/download/audio/2021/11/25/audio_10bd41749a.mp3?filename=sad-cinematic-piano-103396.mp3",
    "https://cdn.pixabay.com/download/audio/2022/09/14/audio_619339fbc7.mp3?filename=sad-and-alone-122235.mp3",
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_4d8b9b0e0a.mp3?filename=sad-piano-music-112199.mp3",
    "https://cdn.pixabay.com/download/audio/2022/06/15/audio_ade8a7c3a9.mp3?filename=sad-piano-111427.mp3",
    "https://cdn.pixabay.com/download/audio/2021/10/25/audio_5d2d9f9f0a.mp3?filename=sad-emotional-piano-101197.mp3",
    "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c8a6501d.mp3?filename=sad-violin-109368.mp3",
    "https://cdn.pixabay.com/download/audio/2022/01/18/audio_6a2bb5f3cc.mp3?filename=sad-cello-108642.mp3",
    "https://cdn.pixabay.com/download/audio/2021/09/01/audio_74a3b8a3d7.mp3?filename=sad-moment-100420.mp3",
]

def load_used():
    if USED_LOG.exists():
        try:
            return json.loads(USED_LOG.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_used(lst):
    MUSIC_DIR.parent.mkdir(parents=True, exist_ok=True)
    USED_LOG.write_text(json.dumps(lst, indent=2), encoding="utf-8")

def download_music(url, out_path):
    try:
        print(f"Downloading SAD: {url.split('/')[-1][:30]}")
        r = requests.get(url, timeout=60, stream=True)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        if out_path.stat().st_size > 10000:
            print(f"OK: {out_path.name} {out_path.stat().st_size} bytes")
            return True
        out_path.unlink(missing_ok=True)
        return False
    except Exception as e:
        print(f"Fail: {e}")
        return False

def ensure_music_for_shayari(shayari_data):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    used = load_used()
    print(f"Used tracks count: {len(used)}")

    # Roz alag - unused local pehle
    all_local = [p for p in MUSIC_DIR.glob("*.mp3") if p.stat().st_size > 10000]
    unused_local = [p for p in all_local if p.name not in used]
    if unused_local:
        chosen = random.choice(unused_local)
        print(f"Using UNIQUE sad: {chosen.name}")
        used.append(chosen.name)
        save_used(used)
        return str(chosen)

    # Naya download
    print("Downloading NEW sad track...")
    for url in random.sample(SAD_MUSIC, len(SAD_MUSIC)):
        fname = f"sad_{random.randint(10000,99999)}.mp3"
        out = MUSIC_DIR / fname
        if download_music(url, out):
            used.append(out.name)
            if len(used) > 20:
                used = [out.name]
            save_used(used)
            return str(out)

    all_mp3 = [p for p in MUSIC_DIR.glob("*.mp3") if p.stat().st_size > 10000]
    if all_mp3:
        chosen = random.choice(all_mp3)
        return str(chosen)
    return None
