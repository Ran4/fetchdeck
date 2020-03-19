import os
from typing import List, Dict, Optional
import re

import requests

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

class MagicCard:
    def __init__(self, name: str, qty: int):
        self.name = name
        self.qty = qty

    def __str__(self) -> str:
        return f"{self.qty}x {self.name}"

    def __repr__(self) -> str:
        return f"<MagicCard name={self.name!r} qty={self.qty}>"


class TappedOutMagicDeckMixin:
    @classmethod
    def from_tappedout_response(cls, raw_dict: Dict):
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

    @classmethod
    def from_tappedout_name(cls, tappedout_deck_name: str) -> "MagicDeck":
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

        return cls.from_tappedout_response(response_dict)



class MagicDeckBase:
    def __init__(
            self,
            cards: List[MagicCard],
            sideboard: Optional[List[MagicCard]],
            name: Optional[str],
            url: Optional[str]
        ):
        self.cards = cards

        self.sideboard: List[MagicCard] = sideboard if sideboard else []
        self.name = name
        self.url = url

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<MagicDeck name={self.name!r}>"

    def __len__(self) -> int:
        """Number of cards in the mainboard
        """
        return self.num_cards

    @property
    def num_cards(self) -> int:
        """Number of cards in the mainboard
        """
        return sum(card.qty for card in self.cards)

    @property
    def num_sideboard_cards(self) -> int:
        """Number of cards in the sideboard
        """
        return sum(card.qty for card in self.sideboard)

    @property
    def total_num_cards(self) -> int:
        return self.num_cards + self.num_sideboard_cards


class MagicDeck(MagicDeckBase, TappedOutMagicDeckMixin):
    pass


def guess_tappedout_deck_name_from_string(s: str) -> str:
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


def get_deck_from_string(s: str) -> MagicDeck:
    tappedout_deck_name = guess_tappedout_deck_name_from_string(s)
    deck: MagicDeck = MagicDeck.from_tappedout_name(tappedout_deck_name)
    print(f"Fetched deck {deck}")
    return deck


if __name__ == "__main__":
    import sys
    s = sys.argv[1]

    deck = get_deck_from_string(s)
