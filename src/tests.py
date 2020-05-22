from tappedout import (
    guess_deck_name_from_string,
    get_tappedout_tapped_cookie_value_from_firefox_sqlite3_db,
)


def test_guess_tappedout_deck_name_from_tappedout_url_string():
    for url, expected in [
            ("http://tappedout.net/mtg-decks/dimir-taxes/", "dimir-taxes"),
            ("http://tappedout.net/mtg-decks/dimir-taxes", "dimir-taxes"),
            ("http://tappedout.net/mtg-decks/a/", "a"),
            ]:
        assert guess_deck_name_from_string(url) == expected


def test_guess_tappedout_deck_name_from_deck_name_string():
    for url, expected in [
            ("dimir-taxes", "dimir-taxes"),
            ("dimir taxes", "dimir-taxes"),
            ]:
        assert guess_deck_name_from_string(url) == expected


def test_get_tappedout_tapped_cookie_value_from_firefox_sqlite3_db():
    tapped = get_tappedout_tapped_cookie_value_from_firefox_sqlite3_db()
    assert tapped
