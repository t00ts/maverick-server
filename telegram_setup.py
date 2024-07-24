from telethon.sync import TelegramClient

import toml

# Load telegram config
with open('config.toml', 'r') as file:
    config = toml.load(file)

tg_api_id = config['telegram']['api_id']
tg_api_hash = config['telegram']['api_hash']

# Create a Telegram client
client = TelegramClient('maverick', tg_api_id, tg_api_hash)

# Connect to Telegram
client.start()

# Get all dialogs (groups and chats)
dialogs = client.get_dialogs()

# Print entity IDs for all groups
for dialog in dialogs:
    if dialog.is_group or dialog.is_channel:
        print(f"Entity ID: {dialog.entity.id}")
        print(f"Name: {dialog.name}")
        print(f"Type: {dialog.entity.__class__.__name__}")
        print("------------------------")

# Disconnect from Telegram
client.disconnect()
