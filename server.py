import asyncio
import websockets
import threading
import aioconsole

import json
import toml
import sys

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from telethon.sync import TelegramClient
from telethon import events

from custom_telegram import parse_telegram_msg
from custom_maverick import process_maverick_msg

# Load config
with open('config.toml', 'r') as file:
    config = toml.load(file)

# Telegram config
tg_api_id = config['telegram']['api_id']
tg_api_hash = config['telegram']['api_hash']
tg_group_entities = config['telegram']['group_entities']

# Basic betting config
betting_host = config['betting']['host']
betting_stake = config['betting']['stake']


# -- WS Server ----------------------------------------------------------------

# Global variable to store the WebSocket server
server = None

class WebSocketServer:

    def __init__(self, host="0.0.0.0", port=5999):
        self.server = None
        self.host = host
        self.port = port
        self.message_queue = None

    async def start_server(self):
        self.message_queue = asyncio.Queue()
        self.server = await websockets.serve(
            self.client_handler, self.host, self.port
        )
        try:
            await self.server.wait_closed()
        except:
            print("Server stopped!", file=sys.stderr)

    def shutdown(self):
        self.server.close()
        print("Server shutdown!", file=sys.stderr)
        asyncio.get_event_loop().stop()

    async def client_handler(self, websocket, path):
        try:
            print(f"Client connected: {websocket.remote_address}", file=sys.stderr)
            # Tasks to concurrently handle sending and receiving messages
            receive_task = asyncio.ensure_future(self.receive_handler(websocket))
            send_task = asyncio.ensure_future(self.send_handler(websocket))
            # Wait for either task to finish
            await asyncio.wait([receive_task, send_task], return_when=asyncio.FIRST_COMPLETED)
        except websockets.ConnectionClosedError:
            print(f"Connection with {websocket.remote_address} closed (1)", file=sys.stderr)
            return

    async def receive_handler(self, websocket):
        while True:
            try:
                message = await websocket.recv()
                if not message:
                    break
                print(highlight(pretty(message), JsonLexer(), TerminalFormatter()), file=sys.stderr, flush=False)
                print("---", file=sys.stderr, flush=False)
                process_maverick_msg(message)
            except websockets.ConnectionClosedError:
                print(f"Connection with {websocket.remote_address} closed (2)", file=sys.stderr)
                return

    async def send_handler(self, websocket):
        while True:
            try:
                message = await self.message_queue.get()
                await websocket.send(message)
            except websockets.ConnectionClosedError:
                print(f"Connection with {websocket.remote_address} closed (3)", file=sys.stderr)
                return

def pretty(string):
    """
    Pretty-prints a JSON string
    """
    try:
        json_data = json.loads(string)
        pretty_json = json.dumps(json_data, indent=2)
        return pretty_json

    except json.JSONDecodeError as e:
        return string


# -- Telegram -----------------------------------------------------------------

# List of matches we've already received a bet for
received_matches = []

# Telegram client
tg_client = TelegramClient('maverick', tg_api_id, tg_api_hash)

async def telegram_feed():
    """
    Subscribes to incoming Telegram messages from the given entity
    and sends them to the processing queue.
    """

    await tg_client.start()

    # Now subscribe to new messages
    tg_client.add_event_handler(process_msg, events.NewMessage(chats=tg_group_entities))
    try:
        await tg_client.run_until_disconnected()
    except:
        print("Telegram feed stopped!", file=sys.stderr)

async def process_msg(msg):
    """
    Process incoming Telegram messages and create the Maverick-compatible
    BetRequest object.
    """

    # Make sure we haven't placed a bet in this match today
    #if cmd['match_teams'] in ignore_matches:
    #    print(f"Bet already placed for {cmd['match_teams']}", file=sys.stderr)
    #    return

    print("Processing new Telegram message: {id}".format(id=msg.id), file=sys.stderr)
    print(msg.text, file=sys.stderr)

    # Parse the Telegram message
    cmd = parse_telegram_msg(msg.text, betting_host, betting_stake)

    # Ignore if we've already received a bet for this match
    match = cmd['place_bet']['bet']['match']
    if match in received_matches:
        print(f"Ignoring. Bet already received for {match}", file=sys.stderr)
        return
    else:
        print(f"New bet received for {match}", file=sys.stderr)
        received_matches.append(match)

    json_command = json.dumps(cmd)
    json_string = json.dumps(cmd, indent=2)
    print(highlight(json_string, JsonLexer(), TerminalFormatter()), file=sys.stderr)

    if hasattr(process_msg, 'server') and process_msg.server:
        await process_msg.server.message_queue.put(json_command)


# -- Stdin --------------------------------------------------------------------

async def async_input(prompt: str) -> str:
    return 

async def stdin_feed():
    while True:
        message = await aioconsole.ainput("> ")
        if message == "quit":
            exit(0)
        if hasattr(process_msg, 'server') and process_msg.server:
            await process_msg.server.message_queue.put(message)

# -- Main ---------------------------------------------------------------------

async def main():

    # Create instances tasks (WebSocket server and data feed)
    websocket_server = WebSocketServer()

    # Store reference to server in process_msg
    process_msg.server = websocket_server

    # Run both tasks concurrently
    try:
        await asyncio.gather(
            websocket_server.start_server(),
            #telegram_feed(),
            stdin_feed(),
        )
    except:
        print("Main loop stopped!", file=sys.stderr)

if __name__ == "__main__":
    # Run the asyncio event loop in a separate thread
    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=loop.run_until_complete, args=(main(),))
    loop_thread.start()

    # Wait for the asyncio event loop to finish
    try:
        loop_thread.join()
    except (KeyboardInterrupt, EOFError):
        print("\nCleaning up and exiting...", file=sys.stderr)
        exit()
