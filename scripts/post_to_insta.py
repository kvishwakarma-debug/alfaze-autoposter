import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

print(f"IG_USER_ID exists: {bool(IG_USER_ID)}")
print(f"ACCESS_TOKEN exists: {bool(ACCESS_TOKEN)}")

if not IG_USER_ID or not ACCESS_TOKEN:
    raise Exception("Secret missing!")

SHAYARIS = [
    "Mohabbat me nahi hai farq jeene aur marne ka,\nUsi ko dekh ke jeete hain jis kafir pe dum nikle",
    "Dil-e-nadaan tujhe hua kya hai,\nAakhir is dard ki dawa kya hai",
    "Bahut kareeb aati ja rahi ho,\nBichadne ka irada kar liya kya?"
]

def create_shayari_image(text):
    img = Image.new('RGB', (1080, 1080), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 55)
    except:
        font = ImageFont.load_default()
    lines = textwrap.wrap(text, width=26)
    y_text = 380
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]
        draw.text(((1080-w)/2, y_text), line, font=font, fill=(255,255,255))
        y_text+=75
    img.save("generated_image.jpg", "JPEG", quality=95)
    print("Image saved")
    return "generated_image.jpg"

def upload_image(image_path):
    print("Uploading to catbox.moe...")
    # CATBOX.MOE - Yehi Instagram ke liye chalta hai!
    try:
        with open(image_path, 'rb') as f:
            data = {"reqtype": "fileupload"}
            files = {"fileToUpload": f}
            r = requests.post("https://catbox.moe/user/api.php", data=data, files=files, timeout=30)
            print(f"Catbox response: {r.text}")
            if r.status_code == 200 and "https://" in r.text:
                url = r.text.strip()
                print(f"SUCCESS URL: {url}")
                return url
    except Exception as e:
        print(f"catbox failed: {e}")

    # Backup: 0x0.st
    try:
        with open(image_path, 'rb') as f:
            r = requests.post("https://0x0.st", files={"file": f}, timeout=30)
            if "https://" in r.text:
                print(f"SUCCESS URL: {r.text.strip()}")
                return r.text.strip()
    except Exception as e:
        print(f"0x0 failed: {e}")

    raise Exception("Upload failed - catbox down")

def post_to_instagram(image_url, caption):
    print(f"Posting: {image_url}")
    url1 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    payload1 = {"image_url": image_url, "caption": caption + "\n\n#shayari", "access_token": ACCESS_TOKEN}
    r1 = requests.post(url1, data=payload1).json()
    print("Container:", r1)
    if "id" not in r1:
        raise Exception(f"Container failed: {r1}")
    creation_id = r1["id"]
    time.sleep(15)
    url2 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    payload2 = {"creation_id": creation_id, "access_token": ACCESS_TOKEN}
    r2 = requests.post(url2, data=payload2).json()
    print("Publish:", r2)
    if "id" not in r2:
        raise Exception(f"Publish failed: {r2}")
    return r2

if __name__ == "__main__":
    shayari = random.choice(SHAYARIS)
    img_path = create_shayari_image(shayari)
    public_url = upload_image(img_path)
    result = post_to_instagram(public_url, shayari)
    print(f"✅ FINAL DONE! Post ID: {result['id']}")
