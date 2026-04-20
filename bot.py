import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ENV VARIABLES
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

users = set()

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text(
        "🔥 Welcome to Dillion Bot\n\n"
        "Send any link (TikTok, IG, YouTube)\n"
        "Or chat with me 🤖"
    )

# STATS COMMAND
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👥 Total Users: {len(users)}")

# DOWNLOAD FUNCTION
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    users.add(update.effective_user.id)

    # LINK DETECTION
    if "http" in text:
        await update.message.reply_text("⏳ Downloading...")

        try:
            await asyncio.to_thread(download_video, text)

            for file in os.listdir():
                if file.startswith("video"):
                    await update.message.reply_video(video=open(file, "rb"))
                    os.remove(file)
                    break

        except:
            await update.message.reply_text("❌ Failed to download")

    else:
        # AI RESPONSE
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": text}]
            )

            reply = response.choices[0].message.content
            await update.message.reply_text(reply)

        except:
            await update.message.reply_text("⚠️ AI error")

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
