import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown
from flask import Flask
from threading import Thread
from keep_alive import keep_alive

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set your bot token and channel IDs from environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN")  # Load the bot token from the .env file
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))  # Convert to integer
DESTINATION_CHANNEL_ID_1 = int(os.getenv("DESTINATION_CHANNEL_ID_1"))
DESTINATION_CHANNEL_ID_2 = int(os.getenv("DESTINATION_CHANNEL_ID_2"))

async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copy messages from source channel to destination channels."""
    if update.channel_post and update.channel_post.chat_id == SOURCE_CHANNEL_ID:
        message = update.channel_post
        try:
            if message.text:
                # Make the message text bold
                bold_text = f"*{escape_markdown(message.text, version=2)}*"
                await context.bot.send_message(
                    chat_id=DESTINATION_CHANNEL_ID_1,
                    text=bold_text,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Text message copied to {DESTINATION_CHANNEL_ID_1}")
                
                await context.bot.send_message(
                    chat_id=DESTINATION_CHANNEL_ID_2,
                    text=bold_text,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Text message copied to {DESTINATION_CHANNEL_ID_2}")
            
            elif message.photo:
                # Handle photo messages with captions
                caption = f"*{escape_markdown(message.caption, version=2)}*" if message.caption else ""
                photo = message.photo[-1]
                await context.bot.send_photo(
                    chat_id=DESTINATION_CHANNEL_ID_1,
                    photo=photo.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Photo message copied to {DESTINATION_CHANNEL_ID_1}")
                
                await context.bot.send_photo(
                    chat_id=DESTINATION_CHANNEL_ID_2,
                    photo=photo.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Photo message copied to {DESTINATION_CHANNEL_ID_2}")
            
            elif message.document:
                # Handle document messages with captions
                caption = f"*{escape_markdown(message.caption, version=2)}*" if message.caption else ""
                await context.bot.send_document(
                    chat_id=DESTINATION_CHANNEL_ID_1,
                    document=message.document.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Document message copied to {DESTINATION_CHANNEL_ID_1}")
                
                await context.bot.send_document(
                    chat_id=DESTINATION_CHANNEL_ID_2,
                    document=message.document.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Document message copied to {DESTINATION_CHANNEL_ID_2}")
            
            elif message.video:
                # Handle video messages with captions
                caption = f"*{escape_markdown(message.caption, version=2)}*" if message.caption else ""
                await context.bot.send_video(
                    chat_id=DESTINATION_CHANNEL_ID_1,
                    video=message.video.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Video message copied to {DESTINATION_CHANNEL_ID_1}")
                
                await context.bot.send_video(
                    chat_id=DESTINATION_CHANNEL_ID_2,
                    video=message.video.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Video message copied to {DESTINATION_CHANNEL_ID_2}")
            
            elif message.voice:
                # Handle voice note messages
                caption = f"*{escape_markdown(message.caption, version=2)}*" if message.caption else ""
                await context.bot.send_voice(
                    chat_id=DESTINATION_CHANNEL_ID_1,
                    voice=message.voice.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Voice message copied to {DESTINATION_CHANNEL_ID_1}")
                
                await context.bot.send_voice(
                    chat_id=DESTINATION_CHANNEL_ID_2,
                    voice=message.voice.file_id,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                logging.info(f"Voice message copied to {DESTINATION_CHANNEL_ID_2}")
        
        except Exception as e:
            logging.error(f"Error copying message: {e}")

if __name__ == "__main__":
    # Start the keep-alive server
    keep_alive()

    # Initialize the Telegram bot
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.Chat(SOURCE_CHANNEL_ID), copy_message))
    
    logging.info("Bot is running...")
    telegram_app.run_polling()
