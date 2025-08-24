# Telegram 2FA Code Generator Bot

This is a simple Telegram bot that generates Two-Factor Authentication (2FA) codes on demand. It acts like a secure, ephemeral TOTP (Time-based One-Time Password) generator, meaning it **does not store any sensitive user data**, including your 2FA secret keys.

The bot also includes a minimalistic Graphical User Interface (GUI) built with Tkinter for easy control (Start/Stop/Hide to Tray) directly from your Windows desktop.

---

## Features

* **On-Demand 2FA Code Generation:** Send your 2FA secret key (Base32 format) or `otpauth://` URI to the bot, and it will immediately generate the current 2FA code.

* **Time Remaining Display:** Along with the code, the bot tells you how many seconds are left until the code refreshes.

* **No Data Storage:** For maximum security, the bot processes your secret key in memory only for a brief moment to generate the code and then discards it. Your keys are never stored on the bot's server or locally.

* **Automatic Key Recognition:** No special commands needed! Just send the key, and the bot will recognize it.

* **Desktop GUI (Windows):** A simple Tkinter interface allows you to:

    * **Start/Stop** the bot.

    * **Hide** the bot window to the system tray (with a cyan square icon).

    * Control the bot from the tray icon's context menu.

---

## How it Works

The bot operates by receiving a 2FA secret key or URI from a user. It then uses the `pyotp` library to calculate the current Time-based One-Time Password based on that key and the current time. This process is identical to how mobile authenticator apps (like Google Authenticator) work. The key is never written to disk or persistently stored; it's used only for the immediate code generation.

The desktop GUI runs the Telegram bot's core logic in a separate **thread**, ensuring the user interface remains responsive.

---

## Setup and Installation

Follow these steps to get your bot up and running:

### 1. Get Your Telegram Bot Token

1.  Open Telegram and search for **`@BotFather`**.

2.  Start a chat with `@BotFather` and send the command `/newbot`.

3.  Follow the instructions: choose a name and a username for your bot.

4.  `@BotFather` will give you an **API token** (e.g., `1234567890:AAH_your_token_here_`). **Keep this token secure!**

### 2. Prepare Your Environment

1.  **Install Python:** If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) (Python 3.8+ is recommended).

2.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/yetazero/2FactorAuthenticationTelegramBot.git](https://github.com/yetazero/2FactorAuthenticationTelegramBot.git)
    cd 2FactorAuthenticationTelegramBot
    ```

3.  **Install Dependencies:** Open your terminal or command prompt in the project directory and run:

    ```bash
    pip install pyTelegramBotAPI pyotp Pillow pystray
    ```

### 3. Configure and Run

1.  **Open `2FA.py`:** Ensure your main Python script is named `2FA.py`. Find the line `BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'` and replace `'YOUR_TELEGRAM_BOT_TOKEN_HERE'` with the actual API token you got from `@BotFather`.

    ```python
    # Example in 2FA.py:
    BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE' 
    ```

2.  **Run `python3 2FA.py`:**

3.  **Run the Bot:** Double-click the `run_bot.bat` file.

A Tkinter GUI window will appear. Click "Start Bot" to activate your Telegram bot. You can also "Hide to Tray" to minimize it to your system tray.

---

## Usage (Telegram)

1.  Find your bot in Telegram by its username (the one you chose with `@BotFather`).

2.  Send `/start` to see the welcome message.

3.  To get a 2FA code, simply send your 2FA secret key (e.g., `JBSWY3DPEHPK3PXP`) or the full `otpauth://` URI (e.g., `otpauth://totp/Example:user?secret=JBSWY3DPEHPK3PXP`).

4.  The bot will reply with the current 2FA code and the time remaining until it refreshes.

---

## Security Disclaimer

**This bot is designed with a "no storage" principle to maximize security.** However, please be aware:

* **You are sending your secret key over Telegram:** While Telegram's chats are encrypted, the key is transmitted. Ensure your Telegram account is secure (use 2FA on your Telegram account too!).

* **The key is processed in memory:** Although not stored, the key is present in your computer's RAM for a brief moment during processing. Ensure the computer running the bot is secure.

* **Use at your own risk:** This project is provided as-is. Users are responsible for understanding and accepting the inherent security implications of transmitting sensitive data.

---

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or find any bugs.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
