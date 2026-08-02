import os, random, requests, time
from PIL import Image, ImageDraw, ImageFont

IG_ID = os.getenv("IG_ID")
TOKEN = os.getenv("IG_TOKEN")

shayaris = [
    "Tumhare lafz me itna sukoon hai,\nKi dil ke dard bhi khamosh ho jate hain.",
    "Alfaz-e-Ulfat likhta hu raat bhar,\nTaaki subah kisi ka dil sambhal jaye.",
    "Mohabbat me wafa ki baat na kar,\nYahan log lafzon se bhi mukar jate hain."
]

caption_text = random.choice(shayaris)
W, H = 1080, 1080
img = Image.new('RGB', (W, H), color=(15,15,15))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
bbox = draw.multiline_textbbox((0,0), caption_text, font=font, align="center")
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
draw.multiline_text(((W-tw)//2,(H-th)//2), caption_text, font=font, fill=(255,255,255), align="center", spacing=15)
img_path = "/tmp/shayari.jpg"
img.save(img_path)

with open(img_path, 'rb') as f:
    r = requests.post("https://catbox.moe/user/api.php", data={"reqtype":"fileupload"}, files={"fileToUpload": f})
    image_url = r.text.strip()

url1 = f"https://graph.facebook.com/v19.0/{IG_ID}/media"
data1 = {"image_url": image_url, "caption": f"{caption_text}\n\n#alfazeulfat #shayari", "access_token": TOKEN}
res1 = requests.post(url1, data=data1).json()
container_id = res1["id"]
time.sleep(5)
url2 = f"https://graph.facebook.com/v19.0/{IG_ID}/media_publish"
requests.post(url2, data={"creation_id": container_id, "access_token": TOKEN})
