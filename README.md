# Maverick Test Server

Boilerplate Python server for [Maverick](https://github.com/t00ts/maverick).

Demonstrates two simple ways of sending instructions:
1. Manually, using the stdin to send commands to Maverick.
2. Fetching messages from a Telegram entity _(e.g. a group)_, parsing them into `BetRequest`s, and forwarding them to Maverick.


## Basic project setup

1. Clone the repo
   * `git clone https://github.com/t00ts/maverick-server`
   * `cd maverick-server`
2. _Optional: Set up a Python virtual environment_
   * `python -m venv venv`
   * `source venv/bin/activate`
3. Install dependencies
   * `pip install -r requirements.txt`


### Initial configuration

1. Fill in your Telegram API ID and Hash in `config.toml`. You can get these from https://my.telegram.org.
2. Run `python telegram_setup.py` to set up your Telegram session and **take note of the entity ID for the group you're interested in subscribing to**.
3. Add that entity ID to your `config.toml`, in the `group_entities` array.
4. Adjust the `stake` for your betting strategy in that same file.
5. Save and close the file.


### Parsing incoming Telegram messages

All incoming messages will be sent to the `parse_telegram_msg` function in the `custom_telegram.py` file. This is where you filter and parse messages, and **construct the `BetRequest` object that will be sent to Maverick**. You'll find an example implementation of this function in the file, which you naturally will need to tailor to your needs, dictated by the format of the messages you receive.

> **💡 Pro tip:** To understand how to construct a valid `BetRequest` JSON object, **run the `betreq` binary** that is **included in your Maverick bundle**. You will be able to create `BetRequest` objects interactively and gain detailed insights into how to build your own.

### Using Maverick responses

All Maverick incoming responses will be sent to the `process_maverick_msg` function in the `custom_maverick.py` file. Here's where you can implement your logic for bet tracking, logging, retry attempts, cashflow management, etc. For more information about Maverick responses, see the [Maverick docs](https://github.com/t00ts/maverick?tab=readme-ov-file#maverick-responses).


## Running the server

Launch two side-by-side terminal sessions:

| **Terminal 1**             | **Terminal 2**       |
|----------------------------|----------------------|
| `./run_server.sh`          | `./server_output.sh` |

## Sending commands manually
You can send commands manually by copying and pasting the `BetRequest` JSON objects you want to send into the console where you're running the server, and pressing enter. This very handy when combined with the `betreq` utility and will prove useful for testing your betting strategy, or for sending commands to Maverick without having to wait for a Telegram message to come through. 


## Connecting Maverick to your server

In Maverick's `config.toml`, set the `addr` of your `[server]` block to point to your running websocket server:

```toml
[server]
addr = "ws://localhost:5999"
max_retries = 10
```

[Run Maverick](https://github.com/t00ts/maverick?tab=readme-ov-file#running-mavierick), and you should see the connection has been established successfully:

```
INFO maverick::server: Connecting to server (ws://localhost:5999/)
INFO maverick::server: Connection established successfully.
```