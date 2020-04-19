from collections import defaultdict
from dataclasses import field
from typing import List, Optional

from pandemic.simulation.model import constants
from pandemic.simulation.model.city_id import Card, EventCard
from pandemic.simulation.model.constants import *


@dataclass
class PlayerState:

    city: int = PLAYER_START
    _city_cards: Set[City] = field(default_factory=set)
    _event_cards: Set[EventCard] = field(default_factory=set)
    _contingency_planner_event_card: Optional[Card] = None
    _contingency_planner_city_card: Optional[Card] = None
    _operations_expert_special_shuttle: bool = True
    _num_cards: int = 0
    _city_colors: Dict[int, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def cards(self) -> Set[Card]:
        return self.city_cards | self.event_cards

    @property
    def city_colors(self) -> Dict[Virus, int]:
        return self._city_colors

    @cards.setter
    def cards(self, value: Set[Card]):
        self.clear_cards()
        self.add_cards(list(value))

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
        if Card.card_type(value) == Card.CITY:
            self._city_colors[constants.CITY_COLORS[value]] += 1
            self._contingency_planner_city_card = value
            self._contingency_planner_event_card = None
        else:
            self._contingency_planner_city_card = None
            self._contingency_planner_event_card = value

    def add_card(self, card: Card):
        if Card.card_type(card) == Card.EVENT:
            self._event_cards.add(card)
            self._num_cards += 1
        elif Card.card_type(card) == Card.CITY:
            self._city_colors[constants.CITY_COLORS[card]] += 1
            self._city_cards.add(card)
            self._num_cards += 1

    def add_cards(self, cards: List[Card]):
        [self.add_card(card) for card in cards]

    def clear_cards(self):
        self._num_cards = 0
        self._city_colors = defaultdict(int)
        self._contingency_planner_event_card: Optional[Card] = None
        self._contingency_planner_city_card: Optional[Card] = None
        self._event_cards.clear()
        self._city_cards.clear()

    def remove_card(self, card: Card) -> bool:
        if Card.card_type(card) == Card.CITY:
            try:
                self._city_cards.remove(card)
                self._num_cards -= 1
                self._city_colors[constants.CITY_COLORS[card]] -= 1
                return True
            except KeyError:
                if card == self._contingency_planner_city_card:
                    self._contingency_planner_city_card = None
                    self._city_colors[constants.CITY_COLORS[card]] -= 1
                    return False
        else:
            try:
                self._event_cards.remove(card)
                self._num_cards -= 1
                return True
            except KeyError:
                if card == self._contingency_planner_event_card:
                    self._contingency_planner_event_card = None
                    return False
                raise KeyError

    def num_cards(self) -> int:
        return self._num_cards

    def used_operations_expert_shuttle_move(self):
        self._operations_expert_special_shuttle = False

    def signal_turn_end(self):
        self._operations_expert_special_shuttle = True

    def operations_expert_has_charter_flight(self) -> bool:
        return self._operations_expert_special_shuttle

    def cards_to_string(self) -> str:
        return " ".join(map(lambda x: str(x), self.cards))
