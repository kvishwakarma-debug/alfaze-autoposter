import os, json, random, gspread
from google.oauth2.service_account import Credentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

def get_sheet():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json: return None
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds).open("Alfaz Collab Tracker").sheet1

def generate_texts(partner):
    day = random.randint(57, 72)
    dm = f"Hi @{partner['username']} 👋\n\nAapka {partner['niche']} wala page dekha, kaafi genuine laga! 👌\nMai @alfaze.ulfat chalata hu - 100 Days Deep Quotes + Chai Shayari.\n\nKya hum week me 1 collab post karein? Day {day} ka quote ready hai.\nDono ki reach 2x hogi, Insta collab ko push karta hai.\n\nInterested ho to bolo, invite bhej du?"
    comments = [f"Content genuine laga @{partner['username']} 👌 Collab ka socha tha, DM dekho ek baar", f"Nice page bro 🔥 {partner['niche']} kaafi accha hai, check DM", f"Bhai @{partner['username']} collab karein? Day {day} ready hai, DM kiya hai"]
    return dm, random.choice(comments)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! /next dabao - Agla target ayega")

async def next_collab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("collab/data/queue.json"):
        await update.message.reply_text("Queue khali hai, kal GitHub Action chalne do.")
        return
    with open("collab/data/queue.json", "r", encoding='utf-8') as f:
        queue = json.load(f)
    if not queue:
        await update.message.reply_text("✅ Aaj ke saare Done!")
        return
    p = queue[0]
    dm, comment = generate_texts(p)
    keyboard = [[InlineKeyboardButton("👤 Profile", url=f"https://instagram.com/{p['username']}"), InlineKeyboardButton("💬 DM Kholo", url=f"https://ig.me/m/{p['username']}")],[InlineKeyboardButton("✅ DM Sent", callback_data=f"done_{p['username']}"), InlineKeyboardButton("🚫 DM Band", callback_data=f"closed_{p['username']}"), InlineKeyboardButton("⏭️ Skip", callback_data=f"skip_{p['username']}")]]
    await update.message.reply_text(f"👉 Target: @{p['username']} ({p['followers']} | {p['niche']})", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    await update.message.reply_text(f"**DM (Copy):**\n`{dm}`", parse_mode='MarkdownV2')
    await update.message.reply_text(f"**COMMENT (Agar DM band ho):**\n`{comment}`", parse_mode='MarkdownV2')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, username = query.data.split("_", 1)
    with open("collab/data/queue.json", "r", encoding='utf-8') as f:
        queue = json.load(f)
    sheet = get_sheet()
    if action == "done":
        queue = [q for q in queue if q['username']!= username]
        if sheet:
            try:
                cell = sheet.find(username)
                sheet.update_cell(cell.row, 7, "done")
            except: pass
        open("collab/data/queue.json", "w", encoding='utf-8').write(json.dumps(queue, indent=2, ensure_ascii=False))
        await query.edit_message_text(f"✅ @{username} Done! /next")
    elif action == "closed":
        queue = [q for q in queue if q['username']!= username]
        if sheet:
            try:
                cell = sheet.find(username)
                sheet.update_cell(cell.row, 7, "dm_closed")
            except: pass
        open("collab/data/queue.json", "w", encoding='utf-8').write(json.dumps(queue, indent=2, ensure_ascii=False))
        await query.edit_message_text(f"🚫 @{username} DM Closed. /next")
    elif action == "skip":
        target = next((q for q in queue if q['username'] == username), None)
        queue = [q for q in queue if q['username']!= username]
        if target: queue.append(target)
        open("collab/data/queue.json", "w", encoding='utf-8').write(json.dumps(queue, indent=2, ensure_ascii=False))
        await query.edit_message_text(f"⏭️ @{username} skipped. /next")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_collab))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
