from typing import List, Dict, Optional
import argparse

import requests

from magic_deck import MagicDeck
import tappedout


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetches a Magic deck from tappedout",
    )

    parser.add_argument(
        "tappedout_deck",
        help="The name or url of a tappedout deck, e.g. \"dimir-taxes\"")

    args = parser.parse_args()

    deck: MagicDeck = tappedout.get_deck_from_string(args.tappedout_deck)
    print(f"Fetched deck {deck}")
