from typing import List, Dict, Optional

import requests

from magic_deck import MagicDeck
import tappedout


def get_deck_from_string(s: str) -> MagicDeck:
    return deck


if __name__ == "__main__":
    import sys
    s = sys.argv[1]

    deck: MagicDeck = tappedout.get_deck_from_string(s)
    print(f"Fetched deck {deck}")
