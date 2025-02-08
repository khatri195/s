import json
import logging
import os
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, 
    CallbackContext, ChatJoinRequestHandler
)
from telegram.error import BadRequest

# Bot Token & Channel Details
TOKEN = '7906386980:AAEzysWsp0bvI7doUbpz5Q2OGN280J1Rz2A'  # Replace with your bot token
CHANNEL_ID = -1002409547209  # Replace with your actual channel ID
BROADCAST_USER_ID = 5142771710  # Admin user ID for broadcasting
USER_IDS_FILE = 'user_ids.json'
NOTIFIED_USERS_FILE = 'notified_users.json'  # New file to track notified users

REMINDER_MESSAGE = (
    "📈 **Daily Trading Signal Reminder**\n\n"
    "Join us every day for **Expert Trading Signals** and maximize your profits! 💰🔥\n\n"
    "Stay ahead in the market with accurate trade insights.\n\n"
    "👉 Join our Signal Channel Now:\n"
    "https://t.me/+j6JaiV_W5k5iZTRl\n\n"
    "Let's win together! 🚀📊"
)

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load or Initialize User IDs
try:
    with open(USER_IDS_FILE, 'r') as f:
        user_ids = json.load(f)
except FileNotFoundError:
    user_ids = []

# Load or Initialize Notified Users
try:
    with open(NOTIFIED_USERS_FILE, 'r') as f:
        notified_users = json.load(f)
except FileNotFoundError:
    notified_users = []

# Save User IDs
def save_user_ids():
    with open(USER_IDS_FILE, 'w') as f:
        json.dump(user_ids, f)

# Save Notified Users
def save_notified_users():
    with open(NOTIFIED_USERS_FILE, 'w') as f:
        json.dump(notified_users, f)

# Start Command Handler
async def start(update: Update, context: CallbackContext):
    """Send the signal channel link when the bot is started and store the user ID."""
    user_id = update.message.from_user.id
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_ids()

    await update.message.reply_text(
        f"Welcome! 🤩 Unlock Hidden Strategies on My Channel!\n\n"
        f"https://t.me/+j6JaiV_W5k5iZTRl\n\n"
        f"💡 This will allow you to earn $200 daily\n\n"
        f"👉 [Join Now](https://t.me/+j6JaiV_W5k5iZTRl)",
        parse_mode="Markdown"
    )

# Broadcast Messages to All Users (Only by Admin)
async def handle_message(update: Update, context: CallbackContext):
    """Handle all incoming messages, including broadcasting messages from the admin to all users."""
    user_id = update.message.from_user.id

    # If the message is from the admin, broadcast it to all users in user_ids.json
    if user_id == BROADCAST_USER_ID:
        if update.message.text:
            for uid in user_ids:
                try:
                    await context.bot.send_message(chat_id=uid, text=update.message.text)
                except Exception as e:
                    logging.error(f"Failed to send message to {uid}: {e}")

        elif update.message.photo:
            photo = update.message.photo[-1].file_id
            caption = update.message.caption if update.message.caption else ""
            for uid in user_ids:
                try:
                    await context.bot.send_photo(chat_id=uid, photo=photo, caption=caption)
                except Exception as e:
                    logging.error(f"Failed to send photo to {uid}: {e}")

# Join Request Handler (Auto Accept)
async def handle_join_request(update: Update, context: CallbackContext):
    """Automatically accept join requests and send a welcome message."""
    chat_join_request = update.chat_join_request
    user_id = chat_join_request.from_user.id
    chat_id = chat_join_request.chat.id

    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_ids()

    try:
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        logging.info(f"Approved join request for user {user_id}")

        # Welcome Message
        caption = (
            f"🚀 Welcome {chat_join_request.from_user.first_name} 🤩 Unlock Hidden Strategies on My Channel! 📊\n\n"
            f"🔥 https://t.me/+j6JaiV_W5k5iZTRl\n\n"
            f"💡 Discover proven methods to earn $200 daily with ease\n\n"
            f"👉 [Join Now](https://t.me/+j6JaiV_W5k5iZTRl)"
        )

        await context.bot.send_message(chat_id=user_id, text=caption, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Failed to handle join request for {user_id}: {e}")

# Check & Notify Users Who Left (Only Once)
async def check_removed_users(context: CallbackContext):
    """Check and notify users who have left the signal channel, but only once."""
    global user_ids, notified_users
    
    for uid in user_ids:
        try:
            # Check if the user is still a member of the channel
            member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=uid)

            if member.status in ['left', 'kicked']:
                logging.info(f"User {uid} has left the channel.")
                
                if uid not in notified_users:
                    await context.bot.send_message(
                        chat_id=uid,
                        text="⚠️ It looks like you’ve left the channel! Don’t miss out on daily signals and profit opportunities. Rejoin now to stay updated: 📈🔥\n"
                        "👉 [Click Here to Rejoin](https://t.me/+j6JaiV_W5k5iZTRl)",
                        parse_mode="Markdown"
                    )
                    notified_users.append(uid)
                    save_notified_users()

        except BadRequest:  # User is no longer in the channel
            if uid not in notified_users:
                await context.bot.send_message(
                    chat_id=uid,
                    text="⚠️ It looks like you’ve left the channel! Don’t miss out on daily signals and profit opportunities. Rejoin now to stay updated: 📈🔥\n"
                    "👉 [Click Here to Rejoin](https://t.me/+j6JaiV_W5k5iZTRl)",
                    parse_mode="Markdown"
                )
                notified_users.append(uid)
                save_notified_users()

        except Exception as e:
            logging.error(f"Error checking membership for user {uid}: {e}")

# Flask App for Render Hosting
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

def run_flask():
    """Run Flask in a separate thread."""
    from threading import Thread
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    thread = Thread(target=run)
    thread.start()

# Main Function to Run the Bot
def main():
    """Start the bot and handle incoming updates."""
    run_flask()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    job_queue = application.job_queue
    job_queue.run_repeating(check_removed_users, interval=60, first=30)  # Every 1 minute

    application.run_polling()

if __name__ == '__main__':
    main()
