import os
import random
import requests
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from SIMPLE_MUSIC import app

# 📥 DOWNLOAD MENU CALLBACK (Button dabane par jo menu khulega)
@app.on_callback_query(filters.regex("download_main_menu"))
async def download_menu_handler(_, query: CallbackQuery):
    try:
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
        await query.answer()
        await query.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        print(f"Callback Error: {e}")


# 📹 VIDEO DOWNLOADER COMMAND (/video)
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
            caption=f"🎬 **Title:** {data.get('title', 'Video')}\n\n✨ Powered by RESSO MUSIC ♪",
            supports_streaming=True
        )

        await msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
