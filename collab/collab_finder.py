import json, os, random, requests, gspread
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials

IST = timezone(timedelta(hours=5, minutes=30))

SEED_PAGES = [
    {"username": "shayari.quotes.love", "followers": "45k", "niche": "Love Shayari"},
    {"username": "urdupoetry.lovers", "followers": "78k", "niche": "Urdu Poetry"},
    {"username": "alfaz_e_dil", "followers": "32k", "niche": "Dard Shayari"},
    {"username": "hindi.shayari.quotes", "followers": "120k", "niche": "Hindi Shayari"},
    {"username": "shayari_junction", "followers": "56k", "niche": "Sad Shayari"},
    {"username": "quotes__hub", "followers": "28k", "niche": "English Quotes"},
    {"username": "deep.lines", "followers": "91k", "niche": "Deep Quotes"},
    {"username": "sukoon_e_alfaz", "followers": "37k", "niche": "Sukoon Shayari"},
    {"username": "the.shayar", "followers": "110k", "niche": "Shayari"},
    {"username": "broken.hearts.quotes", "followers": "41k", "niche": "Breakup"},
]

def get_sheet():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json: return None
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open("Alfaz Collab Tracker").sheet1

def main():
    os.makedirs("collab/data", exist_ok=True)
    now_ist = datetime.now(IST)
    sheet = get_sheet()

    done_usernames = set()
    if sheet:
        try:
            records = sheet.get_all_records()
            done_usernames = {r['Username'] for r in records if r['Username']}
        except: pass

    available = [p for p in SEED_PAGES if p['username'] not in done_usernames]
    if len(available) < 5: available = SEED_PAGES

    today_targets = random.sample(available, 5)

    with open("collab/data/queue.json", "w", encoding="utf-8") as f:
        json.dump(today_targets, f, indent=2, ensure_ascii=False)

    if sheet:
        for p in today_targets:
            row = [now_ist.strftime("%d-%m-%Y %I:%M %p IST"), p['username'], p['followers'], p['niche'], f"https://instagram.com/{p['username']}", "", "pending", ""]
            try: sheet.append_row(row)
            except Exception as e: print(e)

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHATID")
    if token and chat_id:
        msg = f"✅ Queue + Sheet Ready - {now_ist.strftime('%d-%m-%Y')}\nTargets: {', '.join(['@'+p['username'] for p in today_targets])}\n/next likho bot me."
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg})

if __name__ == "__main__":
    main()
