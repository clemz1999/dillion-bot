import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# =========================
# ENV VARIABLES
# =========================
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("❌ TOKEN missing")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# MEMORY (simple)
# =========================
users = set()

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text(
        "🔥 Welcome to Dillion\n\n"
        "📥 Send any link to download\n"
        "🤖 Or chat with AI\n\n"
        "/stats - see users"
    )

# =========================
# STATS COMMAND
# =========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👥 Users: {len(users)}")

# =========================
# DOWNLOAD FUNCTION
# =========================
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# =========================
# MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    users.add(update.effective_user.id)

    # DOWNLOAD MODE
    if "http" in text:
        await update.message.reply_text("⏳ Downloading...")

        try:
            await asyncio.to_thread(download_video, text)

            for file in os.listdir():
                if file.startswith("video"):
                    await update.message.reply_video(video=open(file, "rb"))
                    os.remove(file)
                    break

        except Exception:
            await update.message.reply_text("❌ Download failed")

    # AI MODE
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are Dillion AI, smart and helpful."},
                    {"role": "user", "content": text}
                ]
            )

            reply = response.choices[0].message.content
            await update.message.reply_text(reply)

        except Exception:
            await update.message.reply_text("⚠️ AI error")

# =========================
# MAIN
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Bot is running...")
app.run_polling()
