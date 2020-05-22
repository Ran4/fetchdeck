import requests
import csv
import re
import os
import sqlite3

from typing import List, Dict, Optional

from magic_deck import MagicDeck, MagicCard


class FirefoxCookieDbNotFound(Exception):
    pass


def _create_copy_of_firefox_cookies_db_file() -> str:
    """
    Raises:
        FirefoxCookieDbNotFound
    """
    FIREFOX_PROFILE_DIR: str = os.path.expanduser(
        "~/.mozilla/firefox/984tbefw.default-release")
    FIREFOX_COOKIES_DB_PATH = f"{FIREFOX_PROFILE_DIR}/cookies.sqlite"
    if not os.path.exists(FIREFOX_COOKIES_DB_PATH):
        raise FirefoxCookieDbNotFound()

    # Copy the db file because the db file will be locked if firefox is open?
    COOKIES_DB_COPY_FILE_PATH = f"{FIREFOX_PROFILE_DIR}/cookies_copy.sqlite"
    command = f"cp {FIREFOX_COOKIES_DB_PATH} {COOKIES_DB_COPY_FILE_PATH}"  # noqa
    os.system(command)

    return COOKIES_DB_COPY_FILE_PATH


def _read_tapped_cookie_value_from_sqlite3_db(db_file_name: str) -> str:
    conn = sqlite3.connect(db_file_name)

    result = conn.cursor().execute("""
SELECT value FROM moz_cookies WHERE host='.tappedout.net' AND name='tapped'
    """.strip()).fetchone()

    if result:
        tapped: str = result[0]
        assert isinstance(tapped, str)
    else:
        raise Exception(
            "Found Firefox cookie db, but could not extract tapped value")

    conn.close()

    return tapped


def get_tappedout_tapped_cookie_value_from_firefox_sqlite3_db() -> str:
    """
    Raises:
        FirefoxCookieDbNotFound
    """
    COOKIES_DB_COPY_FILE_PATH = _create_copy_of_firefox_cookies_db_file()

    tapped = _read_tapped_cookie_value_from_sqlite3_db(
        COOKIES_DB_COPY_FILE_PATH)

    # Remove the copy of the cookie db so it's not lying around
    os.system(f"rm {COOKIES_DB_COPY_FILE_PATH}")

    return tapped


def get_tappedout_tapped_cookie_value() -> str:
    """
    In order to call tappedout's api, you need to set the "tapped" cookie.
    This program can read this value either from environment variables or by
    reading it from the sqlite3 database file that firefox uses to store
    cookies. This assumes that the user uses firefox and has logged in to
    tappedout using firefox.
    """
    try:
        tappedout_tapped_token = os.environ["TAPPEDOUT_TAPPED_TOKEN"]
        assert tappedout_tapped_token  # Make sure it's not empty
        return tappedout_tapped_token
    except KeyError:
        try:
            return get_tappedout_tapped_cookie_value_from_firefox_sqlite3_db()
        except FirefoxCookieDbNotFound:
            pass

    print("Please set TAPPEDOUT_TAPPED_TOKEN to the value of the 'tapped'"
          "cookie (which you can get from your browser).")
    print("E.g. "
          "`export TAPPEDOUT_TAPPED_TOKEN=oq3m4xn76ax3pqjj23m1qxpqjmd3o1q8`")
    exit(2)


tapped_cookie_value: str = get_tappedout_tapped_cookie_value()


def _get_deck_from_tappedout_response(raw_dict: Dict):
    """
    An example json response can be found at:

        assets/example_tappedout_deck_response.json
    """
    d = raw_dict

    # `inventory` is a list like `[cardname, {"b": "main", "qty": 1}]`
    inventory: List[List] = d["inventory"]

    cards: List[MagicCard] = []
    sideboard: List[MagicCard] = []
    for inventory_item in inventory:
        card_name, qty_and_board_dict = inventory_item
        board = qty_and_board_dict["b"]
        qty = qty_and_board_dict["qty"]

        if board == "main":
            cards.append(MagicCard(name=card_name, qty=qty))
        elif board == "side":
            sideboard.append(MagicCard(name=card_name, qty=qty))
        else:
            raise Exception(
                f"Unknown board type {board} in untapped json response {d}")

    return MagicDeck(
        cards=cards,
        sideboard=sideboard,
        name=d["name"],
        url=d["url"],
    )


def get_deck_from_name(tappedout_deck_name: str) -> "MagicDeck":
    print("Retrieving this tappedout deck:", tappedout_deck_name)
    tappedout_api_deck_url: str = \
        f"http://tappedout.net/api/collection/collection%3Adeck/{tappedout_deck_name}/"  # noqa

    response = requests.get(
        tappedout_api_deck_url,
        cookies={"tapped": tapped_cookie_value})

    if response.status_code != 200:
        raise Exception(
            "Could not retrieve deck from tappedout. "
            f"Status code: {response.status_code}, text: {response.text}")

    response_dict = response.json()

    return _get_deck_from_tappedout_response(response_dict)


def guess_deck_name_from_string(s: str) -> str:
    """
    "http://tappedout.net/mtg-decks/dimir-taxes/" -> "dimir-taxes"
    "dimir taxes" -> "dimir-taxes"
    "dimir-taxes" -> "dimir-taxes"
    """
    if "/tappedout.net/mtg-decks" in s:
        if not s.endswith("/"):
            s += "/"
        match = re.match(
            "https?://tappedout.net/mtg-decks/(?P<deck_name>.+)/", s)

        if match:
            try:
                return match.group("deck_name")
            except IndexError:
                pass

        raise Exception(
            f"Could not guess tappedout deck name from string '{s}'")
    else:
        # "dimir taxes" -> "dimir-taxes"
        return s.replace(" ", "-")


def get_deck_from_string(s: str) -> "MagicDeck":
    """
    Arguments:
        s: A string that can look like any of the following formats:
            * http://tappedout.net/mtg-decks/dimir-taxes/
            * dimir-taxes
            * dimir taxes
    Returns:
        The MagicDeck, retrieved from tappedout.net
    """
    return get_deck_from_name(guess_deck_name_from_string(s))
