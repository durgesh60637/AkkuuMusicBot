pyrogram
tgcrypto
pytgcalls
ffmpeg-python
yt-dlp

pip install -r requirements.txt

import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream, InputStream
import yt_dlp as youtube_dl
from config import BOT_TOKEN, API_ID, API_HASH, STRING_SESSION

app = Client(
    "MusicBot",
    bot_token=8285747706:AAFNfSGjTid3RMdU3uHlOufxsZd4ZwL5SGc,
    api_id=34739668,
    api_hash=8058fbd035b70ce2069aa517d0f9edb7,
    session_string=BQISFdQAOAs2qQ5G9NLcqX9l_nBJSLh1jfQZFz0c7ZA7YYH0od3XCBcSvywSwBQhB1IiZkthMXdvmsX_x1rsV80ft49YYmdKuiPXW5TyoiwjXImtDO9-bp9eN_aVBtzAVJX1LFIdY5k9VlvAMA69CZPQ1wjv4fy1gdqz0S9wZJ1otB43MWIkWGTA4M8U6RJsOKEkTpVp9q0TEslbgmtBU0r82mPVFr9oM4fyEhqkffb6EARhnLrf3OhN2CAN8O3gAiQSZkFpKWxgHw-MpdD0a0vSWTb1ifBWl5uRB-5l4VvkbU43AvDkQfZQpS81MNPsbeLafxVyMmiKjjHIYzt--lla5LEcTAAAAAHyX8VgAA
)

pytgcalls = PyTgCalls(app)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("🎵 Akkuu Music Bot Ready!\nUse /play <YouTube URL> to play music.")

@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.text.split()) < 2:
        await message.reply_text("❌ Please provide a YouTube link.\nExample: /play https://youtube.com/...")
        return
    url = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    ydl_opts = {"format": "bestaudio"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
    await pytgcalls.join_group_call(chat_id, InputStream(InputAudioStream(audio_url)))
    await message.reply_text(f"▶️ Playing: {info['title']}")

@app.on_message(filters.command("pause"))
async def pause(_, message):
    await pytgcalls.pause_stream(message.chat.id)
    await message.reply_text("⏸ Paused.")

@app.on_message(filters.command("resume"))
async def resume(_, message):
    await pytgcalls.resume_stream(message.chat.id)
    await message.reply_text("▶️ Resumed.")

@app.on_message(filters.command("stop"))
async def stop(_, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply_text("⏹ Stopped.")

print("Bot is starting... 🎵")
app.run()
