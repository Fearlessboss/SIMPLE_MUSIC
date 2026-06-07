import os
import random
import requests
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from SIMPLE_MUSIC import app

# 📹 VIDEO DOWNLOADER COMMAND (/video ya /vid)
@app.on_message(filters.command(["video", "vid"]))
async def video_downloader(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a video URL.\n\nExample:\n/video Any_video_url")

    video_url = message.text.split(None, 1)[1]
    msg = await message.reply("🔍 Fetching video...")

    payload = {
        "url": video_url,
        "token": "c99f113fab0762d216b4545e5c3d615eefb30f0975fe107caab629d17e51b52d"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14)",
    }

    try:
        r = requests.post("https://allvideodownloader.cc/wp-json/aio-dl/video-data/", data=payload, headers=headers)
        data = r.json()

        if "medias" not in data or not data["medias"]:
            return await msg.edit("❌ No downloadable video found.")

        best_video = sorted(data["medias"], key=lambda x: x.get("quality", ""), reverse=True)[0]
        video_link = best_video["url"]

        await msg.edit("⬇️ Downloading video...")
        file_name = f"video_{message.from_user.id}_{random.randint(1000, 9999)}.mp4"
        
        with requests.get(video_link, stream=True) as v:
            with open(file_name, "wb") as f:
                for chunk in v.iter_content(chunk_size=8192):
                    f.write(chunk)

        await msg.edit("📤 Uploading video to Telegram...")
        await app.send_video(
            chat_id=message.chat.id,
            video=file_name,
            caption=f"🎬 **Title:** {data.get('title', 'Video')}\n\n✨ Powered by SENO X MUSIC ♪",
            supports_streaming=True
        )

        await msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)


# 🎵 SONG DOWNLOADER COMMAND (/song)
@app.on_message(filters.command(["song"]))
async def audio_downloader(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Please provide a song URL.\n\nExample:\n/song Any_audio_url")

    audio_url = message.text.split(None, 1)[1]
    msg = await message.reply("🔍 Fetching audio...")

    payload = {
        "url": audio_url,
        "token": "c99f113fab0762d216b4545e5c3d615eefb30f0975fe107caab629d17e51b52d"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14)",
    }

    try:
        r = requests.post("https://allvideodownloader.cc/wp-json/aio-dl/video-data/", data=payload, headers=headers)
        data = r.json()

        if "medias" not in data or not data["medias"]:
            return await msg.edit("❌ No downloadable audio found.")

        audio_media = None
        for m in data["medias"]:
            if m.get("extension") == "mp3" or m.get("audioAvailable") == True:
                audio_media = m
                break
        
        if not audio_media:
            audio_media = sorted(data["medias"], key=lambda x: x.get("quality", ""))[0]

        audio_link = audio_media["url"]
        await msg.edit("⬇️ Downloading audio...")

        file_name = f"audio_{message.from_user.id}_{random.randint(1000, 9999)}.mp3"
        
        with requests.get(audio_link, stream=True) as a:
            with open(file_name, "wb") as f:
                for chunk in a.iter_content(chunk_size=8192):
                    f.write(chunk)

        await msg.edit("📤 Uploading audio to Telegram...")
        await app.send_audio(
            chat_id=message.chat.id,
            audio=file_name,
            title=data.get('title', 'Audio'),
            performer="SENO X MUSIC",
            caption=f"🎵 **Song:** {data.get('title', 'Audio')}\n\n✨ Powered by SENO X MUSIC ♪"
        )

        await msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)


# 📥 DOWNLOAD MENU CALLBACK (Button dabane par kya khulega)
@app.on_callback_query(filters.regex("download_main_menu"))
async def download_menu_handler(_, query: CallbackQuery):
    text = (
        "**📥 DOWNLOAD COMMANDS MENU**\n\n"
        "Aap niche diye gaye tareeqon se koi bhi safe media download kar sakte hain:\n\n"
        "🎵 **For Audio/MP3:**\n"
        "`/song <link>` (Example: `/song https://youtube.com/...`)\n\n"
        "📹 **For Video (720p):**\n"
        "`/video <link>` (Example: `/video https://instagram.com/...`)\n\n"
        "⚠️ _Note: Bade files Telegram ke limits ki wajah se thoda waqt le sakte hain._"
    )
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="🏡 Back To Home", callback_data="home")
            ]
        ]
    )
    
    await query.message.edit_text(text, reply_markup=keyboard)
