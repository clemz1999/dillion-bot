import yt_dlp
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Dillion AI PRO is LIVE\n\nSend a link or ask anything 🤖"
    )

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ AI error"

def download_video(url):
    ydl_opts = {
        'outtmpl': 'video_%(id)s.%(ext)s',
        'format': 'best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "http" in text:
        await update.message.reply_text("⏳ Processing...")

        try:
            await asyncio.to_thread(download_video, text)

            file_path = None
            for file in os.listdir():
                if file.startswith("video_"):
                    file_path = file
                    break

            if file_path:
                await update.message.reply_video(video=open(file_path, 'rb'))

                ai = ask_ai(f"Create caption and hashtags for: {text}")
                await update.message.reply_text(ai)

                os.remove(file_path)

        except:
            await update.message.reply_text("❌ Failed")

    else:
        ai = ask_ai(text)
        await update.message.reply_text(ai)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
