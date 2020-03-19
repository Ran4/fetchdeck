import requests
import re
import os

from typing import List, Dict, Optional

from magic_deck import MagicDeck, MagicCard

def get_tappedout_cookies_string() -> str:
    try:
        return os.environ["TAPPEDOUT_COOKIES_STRING"]
    except KeyError:
        print("Please copy-paste TAPPEDOUT_COOKIES_STRING from your browses.")
        print("E.g. export TAPPEDOUT_COOKIES_STRING=\"__cfduid=asd1249123; csrftoken=Xyy4904Xfasd132F; _ga=GA1.2.49430.123; _cb_ls=1; _cb=lBrasd; _chartbeat2=.493.sa.03.9-.2; tapped=43; _gid=GA1.2.31199999.3484313166; adblocker=1; _cb_svref=null\"")  # noqa
        exit(2)

def get_tappedout_cookies_dict() -> Dict:
    tappedout_cookies_string = get_tappedout_cookies_string()
    tappedout_cookies_items = [x.strip().split("=")
                                for x in tappedout_cookies_string.split(";")]
    assert all(len(item) == 2 for item in tappedout_cookies_items), \
        f"Invalid tappedout_cookies_string {tappedout_cookies_string}"
    return {cookie_name: cookie_value
            for cookie_name, cookie_value in tappedout_cookies_items}

tappedout_cookies_dict = get_tappedout_cookies_dict()


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
    tappedout_api_deck_url: str = \
        f"http://tappedout.net/api/collection/collection%3Adeck/{tappedout_deck_name}/"  # noqa

    response = requests.get(
        tappedout_api_deck_url,
        cookies=tappedout_cookies_dict)

    if response.status_code != 200:
        raise Exception(
            "Could not retrieve deck from tappedout. "
            f"Status code: {response.status_code}, text: {response.text}")

    response_dict = response.json()

    return _get_deck_from_tappedout_response(response_dict)


def guess_deck_name_from_string(s: str) -> str:
    # "http://tappedout.net/mtg-decks/dimir-taxes/" -> "dimir-taxes"
    if "/tappedout.net/mtg-decks" in s:
        match = re.match(
            "http://tappedout.net/mtg-decks/(?P<deck_name>.+)/", s)

        if match:
            try:
                return match.group("deck_name")
            except IndexError:
                pass

        raise Exception(
            f"Could not guess tappedout deck name from string {s}")
    else:
        return s.replace(" ", "-")


def get_deck_from_string(s: str) -> "MagicDeck":
    return get_deck_from_name(guess_deck_name_from_string(s))
