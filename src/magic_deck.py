from typing import List, Dict, Optional

Qty = int

CARD_FORMAT_X = "x"  # e.g. "4x Shock"
CARD_FORMAT_NUMBERS = "numbers"  # e.g. "4 shock"
POSSIBLE_FORMATS = [CARD_FORMAT_X, CARD_FORMAT_NUMBERS]


class MagicCard:
    def __init__(self, name: str, qty: Qty):
        assert isinstance(name, str)
        assert isinstance(qty, int)

        self.name = name
        self.qty = qty

    def __str__(self) -> str:
        return self.format(format=CARD_FORMAT_X)

    def format(self, format: str) -> str:
        if format == CARD_FORMAT_X:
            return f"{self.qty}x {self.name}"
        elif format == CARD_FORMAT_NUMBERS:
            return f"{self.qty} {self.name}"
        else:
            raise Exception(
                "format must be one of " +
                ','.join(f'"{format}"' for format in POSSIBLE_FORMATS))

    def __repr__(self) -> str:
        return f"<MagicCard name={self.name!r} qty={self.qty}>"


class MagicDeck:
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
