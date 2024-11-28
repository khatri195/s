import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set your bot token and channel IDs directly
TOKEN = "7970351713:AAH37a7sXeLODhk5lE-Kv-rHZfT5rf27zNk"  # Your bot token
SOURCE_CHANNEL_ID =  -1001809394454 # Your source channel ID
DESTINATION_CHANNEL_ID_1 = -1001963308685 # Your first destination channel ID
DESTINATION_CHANNEL_ID_2 = -1001710350211  # Your second destination channel ID

# Function to detect if a message contains a link
def contains_link(text):
    url_pattern = r'(http[s]?://\S+|www\.\S+)'
    return bool(re.search(url_pattern, text))

async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copy messages from source channel to destination channels."""
    if update.channel_post and update.channel_post.chat_id == SOURCE_CHANNEL_ID:
        if update.channel_post.text:
            if not contains_link(update.channel_post.text):
                try:
                    await context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID_1, text=update.channel_post.text)
                    logging.info(f"Text message copied to {DESTINATION_CHANNEL_ID_1}")
                    await context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID_2, text=update.channel_post.text)
                    logging.info(f"Text message copied to {DESTINATION_CHANNEL_ID_2}")
                except Exception as e:
                    logging.error(f"Error copying text message: {e}")
            else:
                logging.info("Text message contains a link. Not copying.")
        elif update.channel_post.photo:
            if not contains_link(update.channel_post.caption if update.channel_post.caption else ""):
                try:
                    photo = update.channel_post.photo[-1]
                    caption = update.channel_post.caption if update.channel_post.caption else ""
                    await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID_1, photo=photo.file_id, caption=caption)
                    logging.info(f"Photo message copied to {DESTINATION_CHANNEL_ID_1}")
                    await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID_2, photo=photo.file_id, caption=caption)
                    logging.info(f"Photo message copied to {DESTINATION_CHANNEL_ID_2}")
                except Exception as e:
                    logging.error(f"Error copying photo message: {e}")
            else:
                logging.info("Photo message contains a link. Not copying.")
        elif update.channel_post.document:
            if not contains_link(update.channel_post.caption if update.channel_post.caption else ""):
                try:
                    caption = update.channel_post.caption if update.channel_post.caption else ""
                    await context.bot.send_document(chat_id=DESTINATION_CHANNEL_ID_1, document=update.channel_post.document.file_id, caption=caption)
                    logging.info(f"Document message copied to {DESTINATION_CHANNEL_ID_1}")
                    await context.bot.send_document(chat_id=DESTINATION_CHANNEL_ID_2, document=update.channel_post.document.file_id, caption=caption)
                    logging.info(f"Document message copied to {DESTINATION_CHANNEL_ID_2}")
                except Exception as e:
                    logging.error(f"Error copying document: {e}")
            else:
                logging.info("Document message contains a link. Not copying.")
        elif update.channel_post.video:
            if not contains_link(update.channel_post.caption if update.channel_post.caption else ""):
                try:
                    caption = update.channel_post.caption if update.channel_post.caption else ""
                    await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID_1, video=update.channel_post.video.file_id, caption=caption)
                    logging.info(f"Video message copied to {DESTINATION_CHANNEL_ID_1}")
                    await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID_2, video=update.channel_post.video.file_id, caption=caption)
                    logging.info(f"Video message copied to {DESTINATION_CHANNEL_ID_2}")
                except Exception as e:
                    logging.error(f"Error copying video: {e}")
            else:
                logging.info("Video message contains a link. Not copying.")

if __name__ == "__main__":
    # Start the keep-alive server
    keep_alive()

    # Initialize the Telegram bot
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.Chat(SOURCE_CHANNEL_ID), copy_message))
    
    logging.info("Bot is running...")
    telegram_app.run_polling()