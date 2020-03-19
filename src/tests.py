from main import guess_tappedout_deck_name_from_string


def test_guess_tappedout_deck_name_from_tappedout_url_string():
    for url, expected in [
            ("http://tappedout.net/mtg-decks/dimir-taxes/", "dimir-taxes"),
            ("http://tappedout.net/mtg-decks/a/", "a"),
            ]:
        assert guess_tappedout_deck_name_from_string(url) == expected


def test_guess_tappedout_deck_name_from_deck_name_string():
    for url, expected in [
            ("dimir-taxes", "dimir-taxes"),
            ("dimir taxes", "dimir-taxes"),
            ]:
        assert guess_tappedout_deck_name_from_string(url) == expected
