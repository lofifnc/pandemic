from typing import List, Set

from pandemic.model.city_id import Card
from pandemic.model.constants import *


class PlayerState:
    def __init__(self):
        self._city = PLAYER_START
        self._cards: Set[Card] = set()

    def get_city(self) -> City:
        return self._city

    def set_city(self, city_id: City):
        self._city = city_id

    def get_cards(self) -> Set[Card]:
        return self._cards.copy()

    def get_city_cards(self) -> Set[City]:
        return {c for c in self._cards if isinstance(c, City)}

    def add_card(self, card: Card):
        self._cards.add(card)

    def add_cards(self, cards: List[Card]):
        self._cards = self._cards.union(cards)

    def remove_card(self, card: Card):
        self._cards.remove(card)

    def num_cards(self) -> int:
        return len(self._cards)
