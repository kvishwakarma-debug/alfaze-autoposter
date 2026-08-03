import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publishers.music_mixer import ensure_music
from publishers.story_publisher import post_to_story
from publishers.facebook_publisher import post_to_fb_reel

import requests, random, time, subprocess, urllib.parse
from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime
from moviepy.editor import ImageClip, AudioFileClip

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
REPO = os.getenv("GITHUB_REPOSITORY")

SHAYARIS = {
17: "सुबह की चाय में तेरी यादों का धुआँ है,\nहर घूँट के साथ तू और याद आता है।",
18: "बारिश, चाय और तुम्हारी बातें,\nतीनों का नशा उतरता ही नहीं है।",
19: "सहरा सी है ये ज़िन्दगी मेरी,\nएक तुम हो जो चाय सी नमी देते हो।",
20: "किताबों के पन्ने पलटते-पलटते,\nएक ख़याल में तुम पलट आते हो।",
21: "छत पर चाय, और ख़यालों में तुम,\nइससे बेहतर सुबह हो ही नहीं सकती।",
22: "जंगल की ख़ामोशी, चाय की गर्मी,\nऔर दिल में बस तुम्हारी नर्मी।",
23: "झील किनारे चाय, और ख़यालों में तुम,\nइससे ज़्यादा सुकून कहाँ मिलेगा यार।",
24: "काम के बोझ में भी सुकून है,\nजब चाय के बहाने तुम याद आते हो।",
25: "गाँव की सुबह, चूल्हे की चाय,\nऔर तुम्हारी यादों की मीठी सी गहराई।",
26: "घाट किनारे चाय, और ज़िन्दगी का ख़याल,\nहर घूँट में छुपा है एक सवाल।",
27: "चलती ट्रेन, खिड़की पर चाय,\nऔर तुम्हारी याद का सफ़र जारी है।",
28: "समुंदर किनारे चाय, और लहरों में तुम,\nइस दिल को और क्या चाहिए, बस तुम।",
29: "कैंटीन की चाय में दोस्ती का ज़ायका है,\nऔर उसी ज़ायके में तुम्हारी कमी का एहसास है।",
30: "अलाव की आँच, हाथों में चाय,\nऔर ख़यालों में बस तेरी ही परछाई।",
31: "सुबह की पहली चाय, और तुम्हारा पहला ख़याल,\nदिन की शुरुआत इससे बेहतर क्या होगी।"
}
BG_PROMPTS = {
17: "early morning balcony chai sunrise, steaming kulhad chai",
18: "rainy window chai monsoon, kulhad chai on windowsill with raindrops",
19: "desert sunset chai, kulhad on sand dune dramatic sky",
20: "old books stack with kulhad chai on wooden table warm light",
21: "rooftop chai sunrise city view, kulhad on ledge",
22: "misty forest morning chai on wooden stump jungle background",
23: "peaceful lake side chai on rock water reflection morning",
24: "office desk laptop kulhad chai work from home cozy",
25: "village chulha morning kulhad chai on mud stove village",
26: "Varanasi ganga ghat morning chai on stone steps",
27: "Indian train window chai kulhad on sill moving blur landscape",
28: "beach sunset chai on sand waves kulhad",
29: "college canteen steel table kulhad chai students blurred behind",
30: "winter bonfire night hands holding kulhad chai near fire sparks",
31: "morning terrace chai with newspaper kulhad steam sunrise"
}
HASHTAGS = {
17: "#SubahKiChai #Yaadein #MorningChai",
18: "#BaarishAurChai #ChaiLove #MonsoonVibes",
19: "#Sehra #ChaiSiNami #ZindagiShayari",
20: "#Kitabein #Khayal #ChaiAurKitaab",
21: "#ChhatParChai #Subah #Sukoon",
22: "#JungleVibes #ChaiKiGarmi #ForestSoul",
23: "#JheelKinare #LakeVibes #Peaceful",
24: "#WorkAndChai #OfficeChai #Sukoon",
25: "#GaonKiSubah #ChulheKiChai #DesiVibes",
26: "#GhatKiChai #Banaras #Zindagi",
27: "#TrainJourney #WindowSeat #ChaiSafar",
28: "#Samundar #BeachChai #Lehrein",
29: "#CanteenChai #Dosti #CollegeDays",
30: "#Alaav #BonfireNights #WinterChai",
31: "#PehliChai #MorningThoughts #ChaiAurKhayal"
}

def create_chai_post(text, day_num):
    prompt = BG_PROMPTS.get(day_num, "kulhad chai cinematic warm light")
    encoded = urllib.parse.quote(prompt + ", photorealistic, warm cinematic, 4k")
    bg_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1350&nologo=true&seed={day_num}"
    r = requests.get(bg_url, timeout=90)
    open("bg.jpg","wb").write(r.content)
    img = Image.open("bg.jpg").convert("RGB").resize((1080,1350))
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", 46)
        font_wm = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", 28)
    except:
        font_main = ImageFont.load_default()
        font_wm = ImageFont.load_default()
    y = 500
    for line in text.split("\n"):
        bbox = draw.textbbox((0,0), line, font=font_main)
        x = (1080-(bbox[2]-bbox[0]))//2
        draw.text((x,y), line, font=font_main, fill="white", stroke_width=4, stroke_fill="black")
        y+=65
    draw.text((35,1300), f"@alfaze.ulfat | Day {day_num}/365", font=font_wm, fill="white", stroke_width=2, stroke_fill="black")
    os.makedirs("public/images", exist_ok=True)
    filename = f"day{day_num}_{int(datetime.now().timestamp())}.jpg"
    filepath = f"public/images/{filename}"
    img.save(filepath, "JPEG", quality=92)
    subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
    subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
    subprocess.run(["git","add",filepath], check=True)
    subprocess.run(["git","commit","-m",f"Add Day {day_num}"], check=True)
    subprocess.run(["git","push"], check=True)
    time.sleep(10)
    return f"https://raw.githubusercontent.com/{REPO}/main/{filepath}", filepath

def image_to_reel(image_path, day_num):
    try:
        music_path = ensure_music()
        out = f"public/images/reel_day{day_num}_{int(datetime.now().timestamp())}.mp4"
        clip = ImageClip(image_path).set_duration(7)
        audio = AudioFileClip(music_path).subclip(0,7).volumex(0.35)
        clip = clip.set_audio(audio)
        clip.write_videofile(out, fps=24, codec='libx264', audio_codec='aac', logger=None)
        subprocess.run(["git","add",out], check=True)
        subprocess.run(["git","commit","-m",f"Add Reel {day_num}"], check=True)
        subprocess.run(["git","push"], check=True)
        time.sleep(10)
        return f"https://raw.githubusercontent.com/{REPO}/main/{out}"
    except Exception as e:
        print("Reel creation failed:", e)
        return None

def make_caption(shayari, day_num):
    tag = HASHTAGS.get(day_num, "#ChaiShayari")
    return f"{shayari}\n\n☕ Chai Aur Khayal - Day {day_num}/365\n\n#ChaiAurKhayal #AlfazeUlfat #Shayari {tag}"

def post_to_instagram(image_url, caption):
    r1 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media", data={"image_url": image_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
    print("Container:", r1)
    if "id" not in r1: raise Exception(r1)
    time.sleep(18)
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish", data={"creation_id": r1["id"], "access_token": ACCESS_TOKEN}).json()
    print("Publish:", r2)
    return r2

if __name__ == "__main__":
    START_DATE = date(2026, 7, 5)
    today_day = (date.today() - START_DATE).days + 1
    if today_day < 17: today_day = 17
    if today_day > 31: today_day = random.choice(list(SHAYARIS.keys()))
    shayari = SHAYARIS.get(today_day, SHAYARIS[29])
    print(f"Posting Day {today_day}")
    public_url, local_path = create_chai_post(shayari, today_day)
    caption = make_caption(shayari, today_day)
    post_to_instagram(public_url, caption)
    # Try Reel/Story/FB
