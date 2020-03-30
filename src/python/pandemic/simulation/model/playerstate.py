from typing import List, Set, Optional

from pandemic.simulation.model.city_id import Card, EventCard
from pandemic.simulation.model.constants import *


class PlayerState:
    def __init__(self):
        self.city = PLAYER_START
        self._city_cards: Set[City] = set()
        self._event_cards: Set[EventCard] = set()
        # character specific state
        self._contingency_planner_event_card: Optional[Card] = None
        self._contingency_planner_city_card: Optional[Card] = None
        self._operations_expert_special_shuttle = True

    @property
    def cards(self) -> Set[Card]:
        return self.city_cards | self.event_cards

    @property
    def city_cards(self) -> Set[City]:
        if self._contingency_planner_city_card:
            return self._city_cards | {self._contingency_planner_city_card}
        return self._city_cards

    @property
    def event_cards(self) -> Set[EventCard]:
        if self._contingency_planner_event_card:
            return self._event_cards | {self._contingency_planner_event_card}
        return self._event_cards

    @property
    def contingency_planner_card(self) -> Optional[Card]:
        if self._contingency_planner_city_card is not None:
            return self._contingency_planner_city_card
        return self._contingency_planner_event_card

    @contingency_planner_card.setter
    def contingency_planner_card(self, value: Card):
        if isinstance(value, City):
            self._contingency_planner_city_card = value
            self._contingency_planner_event_card = None
        else:
            self._contingency_planner_city_card = None
            self._contingency_planner_event_card = value

    def add_card(self, card: Card):
        if isinstance(card, EventCard):
            self._event_cards.add(card)
        elif card:
            self._city_cards.add(card)

    def add_cards(self, cards: List[Card]):
        [self.add_card(card) for card in cards]

    def clear_cards(self):
        self._event_cards.clear()
        self._city_cards.clear()

    def remove_card(self, card: Card) -> bool:
        if isinstance(card, City):
            try:
                self._city_cards.remove(card)
                return True
            except KeyError:
                if card == self._contingency_planner_city_card:
                    self._contingency_planner_city_card = None
                    return False
        else:
            try:
                self._event_cards.remove(card)
                return True
            except KeyError:
                if card == self._contingency_planner_event_card:
                    self._contingency_planner_event_card = None
                    return False
                raise KeyError

    def num_cards(self) -> int:
        return len(self.event_cards) + len(self.city_cards)

    def used_operations_expert_shuttle_move(self):
        self._operations_expert_special_shuttle = False

    def signal_turn_end(self):
        self._operations_expert_special_shuttle = True

    def operations_expert_has_charter_flight(self) -> bool:
        return self._operations_expert_special_shuttle

    def cards_to_string(self) -> str:
        return " ".join(map(lambda x: x.name.lower(), self.cards))
