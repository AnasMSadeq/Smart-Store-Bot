# Smart Store Telegram Bot

A Python-based Telegram bot designed to automate e-commerce order processing. It handles customer interactions, manages a shopping cart state, and logs all orders directly to Google Sheets in real-time.

## Features

- **Cart Management:** Stateful tracking of user sessions, allowing customers to browse products, add items to a cart, and checkout seamlessly.
- **Google Sheets Integration:** Automatically logs confirmed orders (Order ID, customer details, items, total price) to a specified Google Sheet.
- **Admin Dashboard:** A restricted admin panel to send broadcast messages to all registered users and view basic system analytics.
- **Data Privacy:** Customer phone numbers and sensitive data are handled securely and masked in external logs.

## Tech Stack

- Python 3.x
- pyTelegramBotAPI
- gspread (Google Sheets API)
- OAuth2 integration

## Screenshots

### 1. User Interface & Main Menu
<!-- Drag and drop the Welcome Message screenshot here -->
<img width="1080" height="2226" alt="IMG_20260714_204153_458" src="https://github.com/user-attachments/assets/24872410-3ee0-4f71-a84b-499326a69111" />

### 2. Order Processing & Cart
<!-- Drag and drop the Invoice and Order ID screenshot here -->
<img width="1080" height="2248" alt="IMG_20260714_204214_427" src="https://github.com/user-attachments/assets/bacbba90-af47-4600-8ae8-3669b466b084" />

### 3. Database Synchronization
<!-- Drag and drop the Google Sheets screenshot here -->
<img width="1920" height="793" alt="lv_0_20260714195609" src="https://github.com/user-attachments/assets/4343c77f-2cc8-4d80-84f8-2891aab32a27" />

### 4. Admin Broadcast Panel
<!-- Drag and drop the Admin Panel screenshot here -->
<img width="1080" height="2220" alt="IMG_20260714_204240_405" src="https://github.com/user-attachments/assets/7108f5bf-d6e4-401c-824d-5dfe2e9d92b0" />

## Installation & Setup

1. Clone this repository:
```bash
git clone https://github.com/AnasMSadeq/Smart-Store-Bot.git
cd Smart-Store-Bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configuration:
- Rename `.env.example` to `.env`.
- Add your environment variables:
```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_admin_id
```
- Place your Google Service Account credentials.json file in the root directory.

4. Run the application:
```bash
python main.py
```

## Contact
- LinkedIn: [Anas M. Sadeq](https://linkedin.com/in/anas-m-sadeq)
- GitHub: [@AnasMSadeq](https://github.com/AnasMSadeq)
