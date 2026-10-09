import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
MessageHandler,
ContextTypes,
filters,
)
from shazamio import Shazam
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
raise RuntimeError("BOT_TOKEN environment variable is missing")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"🎵 Welcome to MelodyCatchBot!\n\n"
"Send me a voice message or audio clip, and I'll try to identify the song."
)

async def identify_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
message = update.message
audio_file = None

```
status = await message.reply_text("🔎 Identifying your music...")

try:
    if message.voice:
        tg_file = await context.bot.get_file(message.voice.file_id)
        audio_file = "voice.ogg"
    elif message.audio:
        tg_file = await context.bot.get_file(message.audio.file_id)
        audio_file = "audio_file"
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("audio/"):
        tg_file = await context.bot.get_file(message.document.file_id)
        audio_file = "audio_file"
    else:
        await status.edit_text("Please send a voice message or an audio file.")
        return

    await tg_file.download_to_drive(audio_file)

    shazam = Shazam()
    result = await shazam.recognize_song(audio_file)

    track = result.get("track")
    if not track:
        await status.edit_text(
            "Sorry, I couldn't identify this song. Please try a clearer or longer clip."
        )
        return

    title = track.get("title", "Unknown title")
    artist = track.get("subtitle", "Unknown artist")
    album = track.get("sections", [{}])[0].get("metadata", [])
    album_name = next(
        (item.get("text") for item in album if item.get("title", "").lower() == "album"),
        "Unknown album",
    )

    images = track.get("images", {})
    cover = images.get("coverarthq") or images.get("coverart")

    query = f"{artist} {title}"
    spotify_url = f"https://open.spotify.com/search/{httpx.QueryParams({'q': query})['q']}"
    soundcloud_url = f"https://soundcloud.com/search/sounds?q={httpx.QueryParams({'q': query})['q']}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Spotify", url=spotify_url),
            InlineKeyboardButton("SoundCloud", url=soundcloud_url),
        ]
    ])

    caption = f"🎵 <b>{title}</b>\n{artist}\n\n💿 {album_name}\n\n🎧 <b>Listen / Find:</b>"

    if cover:
        await message.reply_photo(
            photo=cover,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    await status.delete()

except Exception:
    logger.exception("Music recognition failed")
    await status.edit_text(
        "Sorry, something went wrong while identifying your music. Please try again later."
    )

finally:
    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)
```

def main():
app = Application.builder().token(BOT_TOKEN).build()

```
app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        identify_song,
    )
)

app.run_polling()
```

if **name** == "**main**":
main()
