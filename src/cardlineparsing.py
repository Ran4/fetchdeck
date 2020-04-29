import re
from typing import List, Iterable

from magic_deck import MagicCard


class InvalidFormat(Exception):
    pass


class LineWasEmpty(InvalidFormat):
    pass


def number_x_name_parser(s: str) -> MagicCard:
    """
    4x shock
    4X shock
    """
    number_and_x_match = re.match(r"(\d+)[x|X] (.+)", s)
    if number_and_x_match:
        qty_string = number_and_x_match.group(1)
        qty = int(qty_string)

        name = number_and_x_match.group(2)
        return MagicCard(name, qty)
    else:
        raise InvalidFormat()


def number_name_parser(s: str) -> MagicCard:
    """
    4 shock
    3 shock
    """
    number_name_match = re.match(r"(\d+) (.+)", s)
    if number_name_match:
        qty_string = number_name_match.group(1)
        qty = int(qty_string)

        name = number_name_match.group(2)
        return MagicCard(name, qty)
    else:
        raise InvalidFormat()


def just_name_parser(s: str) -> MagicCard:
    """
    shock
    """
    name = s.strip()
    qty = 1

    if not name:
        raise LineWasEmpty()
    return MagicCard(name, qty)


def try_parse_card_line(s: str) -> MagicCard:
    """
    Raises: InvalidFormat

    Tries multiple card line parsers until one works
    >>> try_parse_card_line("4x shock")
    >>> try_parse_card_line("4 shock")
    >>> try_parse_card_line("shock")
    >>> try_parse_card_line("")
    """
    s = s.strip()

    card_line_parsers = [
        number_x_name_parser,
        number_name_parser,
        just_name_parser,
    ]

    for card_line_parser in card_line_parsers:
        try:
            return card_line_parser(s)
        except InvalidFormat as e:
            # If the line is empty we just raise directly
            if isinstance(e, LineWasEmpty):
                raise e
    else:
        raise InvalidFormat(f"Could not parse magic card line {repr(s)}")


def parse_card_lines(card_lines: Iterable[str]) -> List[MagicCard]:
    magic_cards = []
    for i, line in enumerate(card_lines):
        line_looks_like_comment: bool = line.strip().startswith("#")
        if line_looks_like_comment:
            continue

        try:
            magic_card = try_parse_card_line(line)
            magic_cards.append(magic_card)
        except InvalidFormat as e:
            if isinstance(e, LineWasEmpty):
                # Skip empty lines
                pass
            else:
                print("ERROR parsing line {i} `{line}`. Skipping.")
    return magic_cards
