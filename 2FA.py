# -*- coding: utf-8 -*-

import telebot
import pyotp
import re
import time
import sys

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot token.
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

# Проверяем, был ли заменен токен-заполнитель
if BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE' or not BOT_TOKEN:
    print("Error: Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' in the script with your actual bot token.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# --- Bot Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command and sends a welcome message."""
    welcome_message = (
        "Hello! I'm your Two-Factor Authentication (2FA) code generator bot.\n\n"
        "**How to use me:**\n"
        "Simply send me your 2FA secret key (Base32 format, e.g., `JBSWY3DPEHPK3PXP`) "
        "or a full `otpauth://` URI. "
        "I will instantly generate the current 2FA code.\n\n"
        "**Security Note:**\n"
        "I **do not store your secret keys**. Every key is processed only in memory "
        "to generate the code and is immediately discarded."
    )
    bot.reply_to(message, welcome_message, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handles all incoming text messages to generate 2FA codes."""
    text = message.text.strip()

    # Try to parse as otpauth:// URI
    try:
        totp_obj = pyotp.parse_uri(text)
        send_otp_response(message, totp_obj)
        return
    except ValueError:
        pass

    # Try to parse as a raw Base32 secret key
    cleaned_text = text.replace(' ', '').upper()
    if re.match(r'^[A-Z2-7]+$', cleaned_text):
        try:
            totp_obj = pyotp.TOTP(cleaned_text)
            send_otp_response(message, totp_obj)
            return
        except Exception:
            bot.reply_to(message, "Could not generate a code. Please ensure it's a valid Base32 secret key.")
            return

    # Fallback error message
    bot.reply_to(message, "Invalid input. Please send a 2FA secret key or an `otpauth://` URI.")

def send_otp_response(message, totp_obj):
    """Generates and sends the OTP code and its remaining validity time."""
    current_otp = totp_obj.now()
    remaining_seconds = totp_obj.interval - (time.time() % totp_obj.interval)
    response_message = (
        f"Your 2FA code is: `{current_otp}`\n"
        f"Refreshes in: {int(remaining_seconds)} seconds."
    )
    bot.reply_to(message, response_message, parse_mode='Markdown')

# --- Main Execution ---

if __name__ == "__main__":
    print("Bot is starting...")
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Bot has stopped.")
