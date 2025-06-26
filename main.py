# main.py
from pyrogram import Client, filters
from pyrogram.types import Message
import re
import json
import logging
import os

logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("nms_forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

TARGETS_FILE = "targets.json"

def load_targets():
    try:
        with open(TARGETS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_targets(targets):
    with open(TARGETS_FILE, "w") as f:
        json.dump(targets, f)

def clean_text(text):
    if not text:
        return ""
    cleaned_text = re.sub(r'@\w+', '', text)
    return cleaned_text.strip()

@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text(
        "👋 Welcome to the NMS Forwarder Bot!\n\n"
        "Commands:\n"
        "/add_target <chat_id>\n"
        "/remove_target <chat_id>\n"
        "/list_targets"
    )

@app.on_message(filters.command("add_target"))
def add_target(client, message):
    targets = load_targets()
    try:
        chat_id = int(message.text.split()[1])
        if chat_id not in targets:
            targets.append(chat_id)
            save_targets(targets)
            message.reply_text(f"✅ Target {chat_id} added!")
        else:
            message.reply_text("⚠️ Already added.")
    except:
        message.reply_text("❌ Provide a valid chat_id.\nExample: /add_target -1001234567890")

@app.on_message(filters.command("remove_target"))
def remove_target(client, message):
    targets = load_targets()
    try:
        chat_id = int(message.text.split()[1])
        if chat_id in targets:
            targets.remove(chat_id)
            save_targets(targets)
            message.reply_text(f"✅ Target {chat_id} removed!")
        else:
            message.reply_text("⚠️ Target not found.")
    except:
        message.reply_text("❌ Provide a valid chat_id.\nExample: /remove_target -1001234567890")

@app.on_message(filters.command("list_targets"))
def list_targets(client, message):
    targets = load_targets()
    if targets:
        message.reply_text("📍 Targets:\n" + "\n".join([str(t) for t in targets]))
    else:
        message.reply_text("ℹ️ No targets yet.")

@app.on_message(filters.chat_type.groups | filters.chat_type.channels | filters.private)
def forward_message(client, message: Message):
    if message.text or message.caption or message.photo or message.video or message.audio or message.document:
        targets = load_targets()
        if not targets:
            return

        try:
            if message.text:
                cleaned_text = clean_text(message.text)
                for target in targets:
                    app.send_message(chat_id=target, text=cleaned_text)

            elif message.caption:
                cleaned_caption = clean_text(message.caption)
                if message.photo:
                    for target in targets:
                        app.send_photo(chat_id=target, photo=message.photo.file_id, caption=cleaned_caption)
                elif message.video:
                    for target in targets:
                        app.send_video(chat_id=target, video=message.video.file_id, caption=cleaned_caption)
                elif message.document:
                    for target in targets:
                        app.send_document(chat_id=target, document=message.document.file_id, caption=cleaned_caption)
                elif message.audio:
                    for target in targets:
                        app.send_audio(chat_id=target, audio=message.audio.file_id, caption=cleaned_caption)

            elif message.photo:
                for target in targets:
                    app.send_photo(chat_id=target, photo=message.photo.file_id)

            elif message.video:
                for target in targets:
                    app.send_video(chat_id=target, video=message.video.file_id)

            elif message.document:
                for target in targets:
                    app.send_document(chat_id=target, document=message.document.file_id)

            elif message.audio:
                for target in targets:
                    app.send_audio(chat_id=target, audio=message.audio.file_id)

        except Exception as e:
            logging.error(f"Error forwarding: {e}")

logging.info("🤖 NMS Forwarder Bot is running...")
app.run()
