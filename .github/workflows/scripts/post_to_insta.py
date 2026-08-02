import os, random, requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

IG_ID = os.getenv("IG_ID")
TOKEN = os.getenv("IG_TOKEN")

shayaris = [
    "Tumhare lafz me itna sukoon hai,\nKi dil ke dard bhi khamosh ho jate hain.",
    "Mohabbat me wafa ki baat na kar,\nYahan log lafzon se bhi mukar jate hain.",
    "Teri khamoshi ka matlab samajh aaya,\nJab apne hi paraye nazar aaye.",
    "Alfaz-e-Ulfat likhta hu raat bhar,\nTaaki subah kisi ka dil sambhal jaye.",
    "Ishq me jeet kar bhi haare hain hum,\nTumhe paa kar bhi tumhare na hue hum."
]

# 1. Shayari pick
caption_text = random.choice(shayaris)
print(f"Selected: {caption_text}")

# 2. Image banao
W, H = 1080, 1080
img = Image.new('RGB', (W, H), color=(15,15,15))
draw = ImageDraw.Draw(img)
# Font - default use karo, Urdu/Hindi support ke liye system font
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 50)
except:
    font = ImageFont.load_default()

# Text center me
bbox = draw.multiline_textbbox((0,0), caption_text, font=font, align="center")
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
x = (W-tw)//2
y = (H-th)//2
draw.multiline_text((x,y), caption_text, font=font, fill=(255,255,255), align="center", spacing=15)

img_path = "/tmp/shayari.jpg"
img.save(img_path)

# 3. Catbox pe upload (Free hosting taaki IG ko URL mile)
with open(img_path, 'rb') as f:
    r = requests.post("https://catbox.moe/user/api.php", data={"reqtype":"fileupload"}, files={"fileToUpload": f})
    image_url = r.text.strip()
print(f"Image URL: {image_url}")

# 4. IG Container banao
caption_final = f"{caption_text}\n\n.\n.\n#alfazeulfat #shayari #urdupoetry #hindi #quotes"
url1 = f"https://graph.facebook.com/v19.0/{IG_ID}/media"
data1 = {"image_url": image_url, "caption": caption_final, "access_token": TOKEN}
res1 = requests.post(url1, data=data1).json()
print("Container:", res1)

if "id" not in res1:
    raise Exception(f"Container failed: {res1}")

container_id = res1["id"]

# 5. Publish karo
import time; time.sleep(5) # IG ko thoda time do image process karne ka
url2 = f"https://graph.facebook.com/v19.0/{IG_ID}/media_publish"
data2 = {"creation_id": container_id, "access_token": TOKEN}
res2 = requests.post(url2, data=data2).json()
print("Publish:", res2)
print("DONE - Posted to @alfaze.ulfat")
