"""
Custom Telegram message parsing functions that convert Telegram messages into
Maverick-compatible commands like `place_bet`.

Feel free to adjust the parsing logic to suit your Telegram message format.

To gain further understanding of the Maverick protocol and its data types,
run the `betreq` utility included in your Maverick bundle using a terminal.
"""

import re
import uuid

def first_regex_match(regex, text):
    """
    Gets the first regex match
    """

    matches = re.finditer(regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            return match.group(groupNum+1)
    return None

def all_regex_matches(regex, text):
    """
    Gets all regex matches
    """

    found = re.findall(regex, text, re.MULTILINE)
    if len(found) == 0:
        return []
    return found[0]


def parse_telegram_msg(msg, betting_host, betting_stake):
    """
    Parse a Telegram message and return a Maverick-compatible BetRequest object.
    """

    msg = msg.replace('*', '')

    # Extract match teams
    regex_match = r"🆚\s+(.*)\s+vs.\s+(.*)"
    match_info = all_regex_matches(regex_match, msg)
    match_teams = [match_info[0], match_info[1]]

    # Extract match score
    regex_score = r"📣(\d+)\s+-\s+(\d+)"
    match_score = all_regex_matches(regex_score, msg)
    score = [int(match_score[0]), int(match_score[1])]

    # Extract bet information
    bet_info_regex = r"Bet:\s+(.*):\s+(.*)"
    bet_info = all_regex_matches(bet_info_regex, msg)
    mkt_and_tf = bet_info[0]

    # Extract timeframe and market
    msg_tfs = ["Fulltime", "1st Half", "2nd Half"]
    mav_tfs = ["FullTime", "FirstHalf", "SecondHalf"]

    timeframe = mav_tfs[0]
    market = "Unknown"

    for i, tf in enumerate(msg_tfs):
        if mkt_and_tf.startswith(tf):
            market = mkt_and_tf.replace(tf, "").strip()
            timeframe = mav_tfs[i]
            break

    # Extract participant (and hcp)
    participant = ""
    hcp = ""

    if market == "Result":
        participant = bet_info[1].split('@')[0].strip()
    elif market == "Asian Handicap":
        regex_asianhcp = r"(.*?)([+-]?\d+\.\d+(?:,[+-]?\d+\.\d+)?)"
        po = all_regex_matches(regex_asianhcp, bet_info[1])
        participant = po[0].strip()
        hcp = list(map(float, po[1].split(',')))

    # Extract odds
    odds = float(bet_info[1].split('@')[1].strip())

    # Create the place_bet command to send to Maverick
    bet_mkt = {}
    if market == "Result":
        bet_mkt = {
            "result": participant
        }
    elif market == "Asian Handicap":
        bet_mkt = {
            "asian_hcp": {
                "line": hcp,
                "score": score,
                "team": participant
            }
        }

    cmd = {
        "place_bet": {
            "bet": {
                "market": bet_mkt,
                "match": match_teams,
                "odds": odds,
                "tf": timeframe
            },
            "host": betting_host,
            "id": str(uuid.uuid4()),
            "stake": betting_stake
        }
    }

    return cmd

