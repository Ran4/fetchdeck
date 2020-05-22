## Usage:

#### Looking up cards

```bash
$ python3 -i src/fetchdeck.py dimir-taxes
>>> deck
<MagicDeck name='Dimir taxes'>
>>> help(deck)
...
>>> for card in deck.cards:
...     print(card)
1x Barren Moor
7x Island
2x Power Leak
4x Psychic Venom
4x Seizures
4x Swamp
```

#### Generating a "buy guide" for a deck

```
# From tappedout.net url
python3 src/howtobuy.py https://tappedout.net/mtg-decks/dimir-taxes

# From tappedout.net deck name
python3 src/howtobuy.py dimir-taxes

# From local file
python3 src/howtobuy.py dimir_taxes.txt
```
