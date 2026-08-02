import os, random, requests, time
from PIL import Image, ImageDraw, ImageFont

IG_ID = os.getenv("IG_ID")
TOKEN = os.getenv("IG_TOKEN")

print(f"DEBUG: IG_ID={IG_ID[:5]}... Token={TOKEN[:10]}...")

shayaris = [
    "Tumhare lafz me itna sukoon hai,\nKi dil ke dard bhi khamosh ho jate hain.",
    "Alfaz-e-Ulfat likhta hu raat bhar,\nTaaki subah kisi ka dil sambhal jaye.",
    "Mohabbat me wafa ki baat na kar,\nYahan log lafzon se bhi mukar jate hain."
]

caption_text = random.choice(shayaris)

# 1. Image banao
W, H = 1080, 1080
img = Image.new('RGB', (W, H), color=(10,10,10))
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
except:
    font = ImageFont.load_default()

bbox = draw.multiline_textbbox((0,0), caption_text, font=font, align="center")
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
draw.multiline_text(((W-tw)//2,(H-th)//2), caption_text, font=font, fill=(255,255,255), align="center", spacing=12)
img_path = "/tmp/shayari.jpg"
img.save(img_path, quality=95)
print("Image saved")

# 2. Upload - new host 0x0.st (Instagram iske URL ko jyada accept karta hai)
with open(img_path, 'rb') as f:
    r = requests.post("https://0x0.st", files={"file": f})
    image_url = r.text.strip()
    print(f"Image URL: {image_url}")

if not image_url.startswith("http"):
    raise Exception(f"Upload failed: {image_url}")

# 3. IG Container
url1 = f"https://graph.facebook.com/v20.0/{IG_ID}/media"
data1 = {"image_url": image_url, "caption": f"{caption_text}\n\n#alfazeulfat #shayari", "access_token": TOKEN}
res1 = requests.post(url1, data=data1).json()
print(f"Container Response: {res1}")

if "id" not in res1:
    print(f"ERROR DETAILS: {res1}")
    raise Exception(f"IG API Error: {res1}")

container_id = res1["id"]
time.sleep(10)

# 4. Publish
url2 = f"https://graph.facebook.com/v20.0/{IG_ID}/media_publish"
data2 = {"creation_id": container_id, "access_token": TOKEN}
res2 = requests.post(url2, data=data2).json()
print(f"Publish Response: {res2}")
print("SUCCESS!")
