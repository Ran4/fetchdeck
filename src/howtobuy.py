"""
Usage:
    python3 src/howtobuy.py assets/golos_decklist.txt --remove assets/cards_rasmus_owns.txt --format x
"""  # noqa
from typing import List
from typing import Counter as CounterType
from collections import Counter
import argparse

from magic_deck import MagicCard, CARD_FORMAT_X, CARD_FORMAT_NUMBERS
import cardlineparsing


def get_cards_from_file_string(s: str) -> List[MagicCard]:
    with open(s) as f:
        card_lines: List[str] = f.read().split("\n")
    cards: List[MagicCard] = cardlineparsing.parse_card_lines(card_lines)
    return cards


def count_cards(cards: List[MagicCard]) -> int:
    return sum(card.qty for card in cards)


def how_to_buy(decklist: str, cards_to_remove_strings: List[str], format: str):
    """
    Arguments:
        decklist: str - String pointing to a text file containing a
            newline-separated list of cards.
        remove: List[str] - A list of strings, each pointing to a text file
            containing a newline-separated list of cards.
    """
    cards_we_want = get_cards_from_file_string(decklist)
    cards_we_want_counter: CounterType[str] = Counter()
    for card in cards_we_want:
        cards_we_want_counter[card.name] += card.qty

    cards_we_have_counter: CounterType[str] = Counter()
    for cards_to_remove_string in cards_to_remove_strings:
        cards = get_cards_from_file_string(cards_to_remove_string)
        for card in cards:
            cards_we_have_counter[card.name] += card.qty

    cards_to_buy_counter: CounterType[str] = Counter()
    cards_we_want_that_we_have_counter: CounterType[str] = Counter()
    for name in cards_we_want_counter:
        qty_needed = cards_we_want_counter[name] - cards_we_have_counter[name]
        if qty_needed > 0:
            cards_to_buy_counter[name] = qty_needed
        elif qty_needed < 0:
            cards_we_want_that_we_have_counter[name] = \
                cards_we_want_counter[name]

    cards_to_buy = [MagicCard(name, qty)
                    for name, qty in cards_to_buy_counter.items()]
    cards_we_want_that_we_have = [
        MagicCard(name, qty)
        for name, qty in cards_we_want_that_we_have_counter.items()]

    print(f"# Cards to buy ({count_cards(cards_to_buy)}):")
    for card_to_buy in cards_to_buy:
        print(card_to_buy.format(format))

    print()
    n = count_cards(cards_we_want_that_we_have)
    print(f"# Cards we already have ({n}):")
    for card_we_want_that_we_had in cards_we_want_that_we_have:
        print("#", card_we_want_that_we_had.format(format))


def main():
    parser = argparse.ArgumentParser(
        description="Helps figuring out what cards to buy",
    )

    parser.add_argument(
        "decklist",
        help="Decklist, given as a text file with a newline-separated list of cards",  # noqa
    )

    parser.add_argument(
        "--remove",
        action="append",
        help="Remove these cards from the listing"
    )

    DEFAULT_CARD_FORMAT = CARD_FORMAT_NUMBERS
    parser.add_argument(
        "--format",
        choices=[CARD_FORMAT_X, CARD_FORMAT_NUMBERS],
        default=DEFAULT_CARD_FORMAT,
        help='Card output format: "4x opt" vs "4 opt". Default: {}'.format(
            DEFAULT_CARD_FORMAT),
    )

    args = parser.parse_args()

    assert isinstance(args.decklist, str), args.decklist

    if args.remove is None:
        args.remove = []
    assert isinstance(args.remove, list), args.remove
    assert all(isinstance(s, str) for s in args.remove)

    how_to_buy(
        decklist=args.decklist,
        cards_to_remove_strings=args.remove,
        format=args.format,
    )


if __name__ == "__main__":
    main()
