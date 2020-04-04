from dataclasses import dataclass
from typing import List, Tuple, Callable, Any, Set

from pandemic.simulation.model.city_id import Card
from pandemic.simulation.model.enums import Character


class Phase:
    SETUP = 0
    ACTIONS = 1
    DRAW_CARDS = 2
    INFECTIONS = 3
    EPIDEMIC = 4
    FORECAST = 5
    MOVE_STATION = 6
    CHOOSE_CARDS = 7
    CURE_VIRUS = 8


@dataclass
class ChooseCardsPhase:

    next_phase: Phase
    cards_to_choose_from: Set[Card]
    count: int
    player: Character
    after: Callable[[Any, Character, List[Card]], None]

    def __post_init__(self):
        self._chosen_cards = list()

    @property
    def chosen_cards(self) -> List[Card]:
        return self._chosen_cards

    def add_chosen_card(self, card: Card):
        self._chosen_cards.append(card)

    def call_after(self, state):
        self.after(state, self.player, self.chosen_cards)
