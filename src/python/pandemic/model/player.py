from typing import List

from pandemic.model.constants import *


class Player:
    def __init__(self):
        self._city = PLAYER_START
        self._cards: List[str] = []

    def get_city_id(self) -> str:
        return self._city

    def set_city(self, city_id: str):
        self._city = city_id

    def get_cards(self) -> List[str]:
        return self._cards.copy()

    def add_card(self, card: str):
        self._cards.append(card)

    def add_cards(self, cards: List[str]):
        self._cards.extend(cards)

    def remove_card(self, card: str):
        self._cards.remove(card)

    def pop_card(self, index: int) -> str:
        return self._cards.pop(index)
