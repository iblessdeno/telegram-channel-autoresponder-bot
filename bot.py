from telethon import types
from telethon import TelegramClient, events, Button
import os
import json
import logging
from dotenv import load_dotenv
from enum import Enum, auto
import asyncio

# Function to ensure all required environment variables are set
def ensure_env_variables():
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'GROUP_ID', 'OWNER_USERNAME']
    env_file = '.env'
    env_vars = {}

    # Load existing variables from .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

    # Check for missing variables and prompt user
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            value = input(f"Please enter the value for {var}: ")
            env_vars[var] = value

    # Save all variables back to .env file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value

# Call this function before loading the environment variables
ensure_env_variables()

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))
OWNER_USERNAME = os.getenv('OWNER_USERNAME')

# Initialize the client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# JSON file to store the comment message and buttons
JSON_FILE = 'bot_config.json'

# Function to load the bot configuration from JSON file
def load_bot_config():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    return {'comment_message': '', 'buttons': []}

# Function to save the bot configuration to JSON file
def save_bot_config(config):
    with open(JSON_FILE, 'w') as f:
        json.dump(config, f)

# Load the initial configuration
bot_config = load_bot_config()
comment_message = bot_config.get('comment_message', '')
comment_buttons = bot_config.get('buttons', [])
temp_message = ''
temp_buttons = []

class MessageSetterState(Enum):
    WAITING_FOR_MESSAGE = auto()
    WAITING_FOR_BUTTONS = auto()

message_setter_state = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    await event.reply("Welcome! I'm a bot that automatically replies to channel messages forwarded to the group with a set message and buttons. Use /setmessage to set the reply message and buttons.")

@bot.on(events.NewMessage(pattern='/setmessage'))
async def set_message_command(event):
    sender = await event.get_sender()
    if sender.username != OWNER_USERNAME.lstrip('@'):
        await event.reply("Sorry, only the owner can set the message.")
        return

    message_setter_state[sender.id] = MessageSetterState.WAITING_FOR_MESSAGE
    await event.reply("Please send the message you want to set.")
    
    global temp_message, temp_buttons
    temp_message = ''
    temp_buttons = []

    @bot.on(events.NewMessage(from_users=sender.id))
    async def message_handler(event):
        global temp_message, temp_buttons
        
        if event.message.text == '/setmessage':
            return  # Ignore the initial command

        if message_setter_state[sender.id] == MessageSetterState.WAITING_FOR_MESSAGE:
            temp_message = event.message.text
            message_setter_state[sender.id] = MessageSetterState.WAITING_FOR_BUTTONS
            await event.reply("Message set. Now you can add buttons. Here are the commands:\n"
                              "/addbutton Button Text | https://example.com - Add a button\n"
                              "/newrow - Start a new row of buttons\n"
                              "/done - Finish adding buttons")
        elif message_setter_state[sender.id] == MessageSetterState.WAITING_FOR_BUTTONS:
            if event.message.text == '/done':
                buttons = [
                    [Button.inline("Confirm", b"confirm_message")],
                    [Button.inline("Cancel", b"cancel_message")]
                ]
                await event.reply(f"Is this the message and buttons you want to set?\n\nMessage: {temp_message}\n\nButtons: {temp_buttons}", buttons=buttons)
                bot.remove_event_handler(message_handler)
                del message_setter_state[sender.id]
            elif event.message.text == '/newrow':
                temp_buttons.append([])
                await event.reply("New row added. Add buttons to this row.")
            elif event.message.text.startswith('/addbutton'):
                parts = event.message.text[len('/addbutton '):].split('|')
                if len(parts) == 2:
                    button_text = parts[0].strip()
                    button_url = parts[1].strip()
                    if not temp_buttons or len(temp_buttons[-1]) >= 3:  # Max 3 buttons per row
                        temp_buttons.append([])
                    temp_buttons[-1].append([button_text, button_url])
                    await event.reply(f"Button added: {button_text}")
                else:
                    await event.reply("Invalid button format. Please use '/addbutton Button Text | https://example.com'")
            else:
                await event.reply("Invalid command. Use /addbutton to add a button, /newrow to start a new row, or /done to finish.")

    # Set a timeout for the message handler
    await asyncio.sleep(300)  # 5 minutes timeout
    bot.remove_event_handler(message_handler)
    if sender.id in message_setter_state:
        del message_setter_state[sender.id]
        await event.reply("Message setting timed out. Please start again with /setmessage if you still want to set a message.")

@bot.on(events.CallbackQuery(pattern=b"confirm_message"))
async def confirm_message(event):
    global temp_message, temp_buttons, comment_message, comment_buttons
    comment_message = temp_message
    comment_buttons = temp_buttons
    bot_config['comment_message'] = comment_message
    bot_config['buttons'] = comment_buttons
    save_bot_config(bot_config)
    logger.info(f"Message set to: {comment_message}")
    logger.info(f"Buttons set to: {comment_buttons}")
    await event.edit("Message and buttons confirmed and set successfully!")
    temp_message = ''
    temp_buttons = []

@bot.on(events.CallbackQuery(pattern=b"cancel_message"))
async def cancel_message(event):
    global temp_message, temp_buttons
    temp_message = ''
    temp_buttons = []
    await event.edit("Message and button setting cancelled.")

@bot.on(events.NewMessage(pattern='/info'))
async def get_info(event):
    sender = await event.get_sender()
    if sender.username != OWNER_USERNAME.lstrip('@'):
        await event.reply("Sorry, only the owner can view this information.")
        return

    info = f"Group ID: {GROUP_ID}\n"
    info += f"Current message: {comment_message or 'Not set'}\n"
    info += f"Current buttons: {comment_buttons or 'Not set'}"
    await event.reply(info)

@bot.on(events.NewMessage(chats=GROUP_ID))
async def handle_new_message(event):
    try:
        chat = await event.get_chat()
        sender = await event.get_sender()
        
        logger.debug(f"New message in chat type: {type(chat).__name__}")
        logger.debug(f"Chat ID: {getattr(chat, 'id', 'Unknown')}")
        logger.debug(f"Sender ID: {getattr(sender, 'id', 'Unknown')}")
        logger.debug(f"Message content: {event.message.text[:50] if event.message.text else 'No text'}...")
        
        if event.message.fwd_from:
            logger.debug(f"Forward info: {event.message.fwd_from}")
            
            is_channel_forward = (
                event.message.fwd_from.from_id and 
                isinstance(event.message.fwd_from.from_id, types.PeerChannel)
            )
            
            if is_channel_forward:
                channel_id = event.message.fwd_from.from_id.channel_id
                logger.info(f"Forwarded message from channel {channel_id}")
                
                # Reload the configuration to get the latest message and buttons
                global comment_message, comment_buttons
                bot_config = load_bot_config()
                comment_message = bot_config.get('comment_message', '')
                comment_buttons = bot_config.get('buttons', [])
                
                if comment_message:
                    try:
                        # Create inline buttons with two columns if there are more than 2 buttons
                        buttons = []
                        flat_buttons = [button for row in comment_buttons for button in row]
                        if len(flat_buttons) > 2:
                            for i in range(0, len(flat_buttons), 2):
                                row = flat_buttons[i:i+2]
                                buttons.append([Button.url(text, url) for text, url in row])
                        else:
                            buttons = [[Button.url(text, url) for text, url in row] for row in comment_buttons]
                        
                        # Reply to the forwarded channel message with the set message and buttons
                        await event.reply(comment_message, buttons=buttons)
                        logger.info(f"Replied to forwarded channel message with: {comment_message} and buttons")
                    except Exception as e:
                        logger.error(f"Error replying to forwarded channel message: {str(e)}")
                else:
                    logger.warning("No message set")
            else:
                logger.debug("Message is forwarded, but not from a channel")
        else:
            logger.debug("Message is not a forwarded message, ignoring")
    except Exception as e:
        logger.error(f"Error in handle_new_message: {str(e)}", exc_info=True)

async def main():
    try:
        group = await bot.get_entity(GROUP_ID)
        logger.info(f"Successfully connected to group: {group.title}")
    except Exception as e:
        logger.error(f"Error connecting to group: {str(e)}", exc_info=True)

    await bot.run_until_disconnected()

print("Bot is running...")
bot.loop.run_until_complete(main())