import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TOKEN missing")

client = OpenAI(api_key=OPENAI_API_KEY)

users = set()

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text("🔥 Dillion Bot Active")

# STATS
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Users: {len(users)}")

# DOWNLOAD
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    users.add(update.effective_user.id)

    if "http" in text:
        await update.message.reply_text("Downloading...")
        try:
            await asyncio.to_thread(download_video, text)

            for file in os.listdir():
                if file.startswith("video"):
                    await update.message.reply_video(video=open(file, "rb"))
                    os.remove(file)
                    break
        except:
            await update.message.reply_text("Download failed")

    else:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            await update.message.reply_text(response.choices[0].message.content)
        except:
            await update.message.reply_text("AI error")

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()
