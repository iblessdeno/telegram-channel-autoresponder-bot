# Channel Forward Auto-Responder Bot for Telegram

## 🤖 About the Bot

The Channel Forward Auto-Responder Bot is a powerful Telegram bot designed to automatically respond to messages forwarded from channels to a specific group. It enhances group engagement by providing customizable responses with interactive buttons.

### Key Features:
- 🔄 Automatic responses to forwarded channel messages
- 🛠 Customizable response messages
- 🔘 Support for inline buttons in responses
- 🔐 Secure environment variable management
- 👤 Owner-only configuration commands

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/channel-forward-auto-responder-bot.git
   cd channel-forward-auto-responder-bot
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - The bot will prompt you for necessary variables on first run, or
   - Create a `.env` file in the project root and add your variables:
     ```
     API_ID=your_api_id
     API_HASH=your_api_hash
     BOT_TOKEN=your_bot_token
     GROUP_ID=your_group_id
     OWNER_USERNAME=@your_username
     ```

### Running the Bot

1. Start the bot:
   ```
   python bot.py
   ```

2. The bot will prompt for any missing environment variables.

3. Once started, the bot will listen for forwarded messages in the specified group.

## 📚 Usage

- `/start`: Displays a welcome message and bot information
- `/setmessage`: Set the auto-response message and buttons (owner only)
- `/info`: View current bot configuration (owner only)

## 🛠 Configuration

Use the `/setmessage` command in a private chat with the bot to configure the auto-response message and buttons. Follow the prompts to set up your custom message and interactive buttons.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/yourusername/channel-forward-auto-responder-bot/issues).

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 📞 Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/yourusername/channel-forward-auto-responder-bot](https://github.com/yourusername/channel-forward-auto-responder-bot)

## 🙏 Acknowledgements

- [Telethon](https://github.com/LonamiWebs/Telethon)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Telegram Bot API](https://core.telegram.org/bots/api)