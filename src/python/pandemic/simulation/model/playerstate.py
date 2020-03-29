from typing import List, Set, Optional

from pandemic.simulation.model.city_id import Card, EventCard
from pandemic.simulation.model.constants import *


class PlayerState:
    def __init__(self):
        self._city = PLAYER_START
        self._cards: Set[Card] = set()
        # character specific state
        self._contingency_planner_card: Optional[Card] = None
        self._operations_expert_special_shuttle = True

    def get_city(self) -> City:
        return self._city

    def set_city(self, city_id: City):
        self._city = city_id

    def get_cards(self) -> Set[Card]:
        return self._cards.copy().union(
            {self._contingency_planner_card} if self._contingency_planner_card is not None else {}
        )

    def get_city_cards(self) -> Set[City]:
        return {c for c in self.get_cards() if isinstance(c, City)}

    def get_event_cards(self) -> Set[EventCard]:
        return {c for c in self.get_cards() if isinstance(c, EventCard)}

    def add_card(self, card: Card):
        self._cards.add(card)

    def add_cards(self, cards: List[Card]):
        self._cards = self._cards.union(cards)

    """
        Remove card from player state
        returns False if card has been removed from special contingency planner stack.
    """

    def remove_card(self, card: Card) -> bool:
        try:
            self._cards.remove(card)
            return True
        except KeyError:
            if card == self._contingency_planner_card:
                self._contingency_planner_card = None
                return False
            else:
                raise KeyError

    def num_cards(self) -> int:
        return len(self.get_cards())

    def get_contingency_planner_card(self) -> Card:
        return self._contingency_planner_card

    def set_contingency_planner_card(self, card: Card):
        self._contingency_planner_card = card

    def used_operations_expert_shuttle_move(self):
        self._operations_expert_special_shuttle = False

    def signal_turn_end(self):
        self._operations_expert_special_shuttle = True

    def operations_expert_has_charter_flight(self) -> bool:
        return self._operations_expert_special_shuttle

    def cards_to_string(self) -> str:
        return " ".join(map(lambda x: x.name.lower(), self.get_cards()))
