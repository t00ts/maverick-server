"""
Logic for handling incoming messages from Maverick.
Feel free to adjust these to your own needs.
"""

import sys


def process_maverick_msg(msg):
    """
    Process a Maverick message
    """

    print("Maverick message:", file=sys.stderr)
    print(msg, file=sys.stderr)

    # TODO: Implement your own parsing logic here

    pass