# Smart Store Bot

A simple Telegram bot for managing store inventory and tracking sales, using Google Sheets as a database.

## Features

- **Cart Management:** Users can add and remove items with auto-calculated totals.
- **Sheets Integration:** Logs orders (order ID, items, total price, customer details) directly to Google Sheets.
- **Admin Broadcast:** Allows the admin to send messages to all users. Uses Sets to prevent duplicate sending and handles blocked instances.
- **Security:** Uses environment variables to protect API tokens.

## Tech Stack

- Python 3
- pyTelegramBotAPI
- gspread & oauth2client

## Setup

1. Clone this repository.
2. Rename `.env.example` to `.env` and add your `BOT_TOKEN` and `ADMIN_ID`.
3. Place your Google Sheets `credentials.json` file in the root directory.
4. Install the required dependencies:

```bash
pip install -r requirements.txt
```
5. Run the bot:

```bash
python main.py
```
