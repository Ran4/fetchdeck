from typing import List, Dict, Optional

import requests

from magic_deck import MagicDeck
import tappedout


def get_deck_from_string(s: str) -> MagicDeck:
    deck: MagicDeck = tappedout.get_deck_from_name(
        tappedout.guess_deck_name_from_string(s))

    print(f"Fetched deck {deck}")
    return deck


if __name__ == "__main__":
    import sys
    s = sys.argv[1]

    deck = get_deck_from_string(s)
