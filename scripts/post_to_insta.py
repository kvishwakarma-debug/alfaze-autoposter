import os, requests, random, textwrap, time, subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# GitHub info auto le lega
REPO = os.getenv("GITHUB_REPOSITORY") # alfaze-autoposter/alfaze-autoposter

SHAYARIS = ["Mohabbat me nahi hai farq jeene aur marne ka,\nUsi ko dekh ke jeete hain jis kafir pe dum nikle"]

def create_and_push_image(text):
    os.makedirs("public/images", exist_ok=True)
    filename = f"post_{int(datetime.now().timestamp())}.jpg"
    filepath = f"public/images/{filename}"

    img = Image.new('RGB', (1080, 1080), color=(18,18,18))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 55)
    except: font = ImageFont.load_default()
    y=380
    for line in textwrap.wrap(text, width=26):
        bbox=draw.textbbox((0,0), line, font=font)
        w=bbox[2]-bbox[0]
        draw.text(((1080-w)/2, y), line, font=font, fill=(255,255,255))
        y+=75
    img.save(filepath, "JPEG", quality=95)
    print(f"Saved locally: {filepath}")

    # Git push
    subprocess.run(["git", "config", "--global", "user.name", "Alfaze Bot"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "bot@alfaze.com"], check=True)
    subprocess.run(["git", "add", filepath], check=True)
    subprocess.run(["git", "commit", "-m", f"Add image {filename}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("Pushed to GitHub")

    # Raw URL banao
    # https://raw.githubusercontent.com/owner/repo/main/public/images/filename
    raw_url = f"https://raw.githubusercontent.com/{REPO}/main/{filepath}"
    print(f"Direct URL: {raw_url}")
    time.sleep(10) # GitHub ko update hone do
    return raw_url

def post_to_instagram(image_url, caption):
    url1 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    r1 = requests.post(url1, data={"image_url": image_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
    print("Container:", r1)
    if "id" not in r1: raise Exception(f"Container failed: {r1}")
    time.sleep(15)
    url2 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    r2 = requests.post(url2, data={"creation_id": r1["id"], "access_token": ACCESS_TOKEN}).json()
    print("Publish:", r2)
    return r2

if __name__ == "__main__":
    shayari = random.choice(SHAYARIS)
    public_url = create_and_push_image(shayari)
    result = post_to_instagram(public_url, shayari)
    print(f"✅ DONE! {result}")
