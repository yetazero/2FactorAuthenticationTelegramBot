import telebot
import pyotp
import re
import time
import os
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
from pystray import Icon as TrayIcon, MenuItem as item

# --- Telegram Bot Configuration ---
# REPLACE 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot API token
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE' 

if not BOT_TOKEN or BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
    print("Error: BOT_TOKEN is not set or is the placeholder. Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot API token.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

bot_running = threading.Event()
bot_thread = None

def run_telegram_bot():
    global bot_running
    print("Bot thread started. Listening for messages...")
    while bot_running.is_set():
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(1)
            if not bot_running.is_set():
                break
    print("Bot thread stopped.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "Hello! I'm your Two-Factor Authentication (2FA) code generator bot.\n\n"
        "**How to use me:**\n"
        "Simply send me your 2FA secret key (Base32 format, e.g., `JBSWY3DPEHPK3PXP`) "
        "or a full `otpauth://` URI. "
        "I will instantly generate the current 2FA code and tell you how much time is left until it refreshes.\n\n"
        "**Important Security Note:**\n"
        "I **do not store any of your secret keys or any other personal data**. "
        "Every time you need a code, you'll need to send me your secret key again. "
        "This ensures maximum security, as your sensitive data never resides on my servers. "
        "Your secret key is processed only in memory for a brief moment to generate the code and then discarded.\n\n"
        "You can view the entire code and make sure it's safe here: [Github - yetazero](https://github.com/yetazero/2FactorAuthenticationTelegramBot)"
    )
    bot.reply_to(message, welcome_message, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()

    try:
        totp_obj = pyotp.parse_uri(text)
        send_otp_response(message, totp_obj)
        return
    except ValueError:
        pass

    cleaned_text = text.replace(' ', '').upper()
    base32_regex = re.compile(r'^[A-Z2-7]+$')

    if base32_regex.match(cleaned_text):
        try:
            totp_obj = pyotp.TOTP(cleaned_text)
            send_otp_response(message, totp_obj)
            return
        except Exception:
            bot.reply_to(message, "I couldn't generate a code from that key. Please ensure it's a valid Base32 secret key.")
            return

    bot.reply_to(message, 
                 "I didn't recognize that as a valid 2FA secret key or `otpauth://` URI. "
                 "Please send your 2FA secret key (e.g., `JBSWY3DPEHPK3PXP`) or the full `otpauth://` URI.")

def send_otp_response(message, totp_obj):
    current_otp = totp_obj.now()
    
    remaining_seconds = totp_obj.interval - (time.time() % totp_obj.interval)
    
    response_message = (
        f"Your current 2FA code is: `{current_otp}`\n"
        f"Time remaining until refresh: {int(remaining_seconds)} seconds."
    )
    bot.reply_to(message, response_message, parse_mode='Markdown')

class BotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Telegram 2FA Bot Controller")
        master.geometry("300x150")
        master.resizable(False, False)

        self.status_label = tk.Label(master, text="Bot Status: Stopped", fg="red")
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Bot", command=self.start_bot)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.hide_button = tk.Button(master, text="Hide to Tray", command=self.hide_to_tray)
        self.hide_button.pack(pady=5)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.tray_icon = None

    def start_bot(self):
        global bot_running, bot_thread
        if not bot_running.is_set():
            bot_running.set()
            bot_thread = threading.Thread(target=run_telegram_bot)
            bot_thread.daemon = True
            bot_thread.start()
            self.status_label.config(text="Bot Status: Running", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            print("Telegram bot started.")
        else:
            messagebox.showinfo("Bot Status", "Bot is already running.")

    def stop_bot(self):
        global bot_running, bot_thread
        if bot_running.is_set():
            bot_running.clear()
            if bot_thread and bot_thread.is_alive():
                print("Waiting for bot thread to stop...")
            self.status_label.config(text="Bot Status: Stopped", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            print("Telegram bot stopping...")
        else:
            messagebox.showinfo("Bot Status", "Bot is not running.")

    def create_image(self, width, height, color):
        image = Image.new('RGB', (width, height), color)
        d = ImageDraw.Draw(image)
        d.rectangle((0, 0, width, height), fill=color)
        return image

    def hide_to_tray(self):
        self.master.withdraw()
        image = self.create_image(64, 64, "cyan")
        
        menu = (
            item('Show Window', self.show_window),
            item('Start Bot', self.start_bot_from_tray),
            item('Stop Bot', self.stop_bot_from_tray),
            item('Exit', self.exit_app)
        )
        self.tray_icon = TrayIcon("telegram_bot", image, "Telegram 2FA Bot", menu)
        self.tray_icon.run()

    def show_window(self, icon, item):
        icon.stop()
        self.master.deiconify()

    def start_bot_from_tray(self, icon, item):
        self.start_bot()
    
    def stop_bot_from_tray(self, icon, item):
        self.stop_bot()

    def exit_app(self, icon, item):
        self.stop_bot()
        icon.stop()
        self.master.quit()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.stop_bot()
            if self.tray_icon:
                self.tray_icon.stop()
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()
