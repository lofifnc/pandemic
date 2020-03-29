import itertools
import logging
from enum import Enum
from random import shuffle, choices
from typing import List, Set, Optional

import numpy as np

from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.model.city_id import EventCard, EpidemicCard, Card
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.model.playerstate import PlayerState


class Phase(Enum):
    SETUP = 0
    ACTIONS = 1
    DRAW_CARDS = 2
    INFECTIONS = 3
    EPIDEMIC = 4
    FORECAST = 5


class State:
    def __init__(self, player_count: int = PLAYER_COUNT):
        self.phase = Phase.SETUP
        # players
        self.players: Dict[Character, PlayerState] = {
            c: PlayerState() for c in choices(list(Character.__members__.values()), k=player_count)
        }

        self.active_player: Character = list(self.players.keys())[0]

        # counters
        self.research_stations = 5
        self.outbreaks = 0
        self._infection_rate_marker = 0
        self.cubes = {
            Virus.YELLOW: COUNT_CUBES,
            Virus.BLACK: COUNT_CUBES,
            Virus.BLUE: COUNT_CUBES,
            Virus.RED: COUNT_CUBES,
        }
        self.actions_left = PLAYER_ACTIONS
        self.cures: Dict[Virus, bool] = {Virus.YELLOW: False, Virus.BLACK: False, Virus.BLUE: False, Virus.RED: False}
        self.one_quiet_night = False
        # phase specific state
        self.drawn_cards = 0
        self.infections_steps = 0

        # cards
        self.cities = create_cities_init_state()
        self.infection_deck: List[City] = list(self.cities.keys())
        shuffle(self.infection_deck)
        self.infection_discard_pile: List[City] = []

        self.player_deck: List[Card] = list(self.cities.keys()) + list(EventCard.__members__.values())
        shuffle(self.player_deck)
        self._serve_player_cards(player_count)
        self._prepare_player_deck()
        self.player_discard_pile: List[Card] = []

        self._add_neighbors_to_city_state()
        self.game_state = GameState.RUNNING

        # infection
        self._init_infection_markers()
        self.previous_phase = self.phase
        self.phase = Phase.ACTIONS

    def _init_infection_markers(self):
        for i in range(3, 0, -1):
            self.__draw_and_infect(i)

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self.infection_deck.pop(1)
            self._infect_city(top_card, times=num_infections)
            self.infection_discard_pile.append(top_card)

    def _infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:

        outbreak_occurred = False
        city_state = self.get_city_state(city)
        if color is None:
            color = city_state.get_color()

        if (
            self._is_city_protected_by_quarantine(city)
            or self.cures[color]
            and (self.cubes[color] == COUNT_CUBES or self._character_location(Character.MEDIC) == city)
        ):
            # virus has been eradicated or city is protected by medic or quarantine expert
            return outbreak_occurred
        for _ in itertools.repeat(None, times):
            outbreak_occurred = self.get_city_state(city).inc_infection(color)
            if outbreak_occurred:
                break

            if self.cubes[color] > 0:
                self.cubes[color] -= 1
            else:
                self.game_state = GameState.LOST

        return outbreak_occurred

    def _character_location(self, char: Character) -> Optional[City]:
        state = self.players.get(char, None)
        return state.get_city() if state else None

    def _is_city_protected_by_quarantine(self, city) -> bool:
        if self.phase != Phase.SETUP and Character.QUARANTINE_SPECIALIST in self.players.keys():
            location = self._character_location(Character.QUARANTINE_SPECIALIST)
            return city in self.cities[location].get_neighbors().union([location])
        return False

    def treat_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        city_state = self.get_city_state(city)
        if color is None:
            color = city_state.get_color()

        for _ in itertools.repeat(None, 3 if self.cures[color] else times):
            is_empty = self.get_city_state(city).dec_infection(color)
            if is_empty:
                break
            self.cubes[color] += 1

        return is_empty

    def draw_cards(self, action: ActionInterface):
        if self.drawn_cards < 2:
            self.players[self.active_player].add_cards(self.draw_card())
            self.drawn_cards += 1
        if self.drawn_cards == 2:
            self.drawn_cards = 0
            self.phase = Phase.INFECTIONS

    def infections(self, action: ActionInterface):
        if self.infections_steps == 0 and self.one_quiet_night:
            pass
        elif self.infections_steps < self.infection_rate():
            top_card = self.infection_deck.pop(0)
            outbreak = self._infect_city(top_card)
            if outbreak:
                self._outbreak(top_card, self.get_city_state(top_card).get_color())
            self.infection_discard_pile.append(top_card)
            self.infections_steps += 1
        if self.infections_steps == self.infection_rate() or self.one_quiet_night:
            self.infections_steps = 0
            if self.infections_steps == 0:
                self.one_quiet_night = False
            [ps.signal_turn_end() for ps in self.players.values()]
            self.active_player = self.get_next_player()
            self.phase = Phase.ACTIONS

    def active_player(self) -> PlayerState:
        return self.players[self.active_player]

    def get_next_player(self) -> Character:
        list_of_player_colors = list(self.players.keys())
        index_of_active_player = list_of_player_colors.index(self.active_player)
        return list_of_player_colors[(index_of_active_player + 1) % len(list_of_player_colors)]

    def _prepare_player_deck(self):
        prepared_deck: List[Card] = []
        city_cards = self.player_deck
        shuffle(city_cards)
        chunks = np.array_split(city_cards, EPIDEMIC_CARDS)
        epidemic_cards = set(EpidemicCard.__members__.values())
        for c in chunks:
            d = list(c)
            d.append(epidemic_cards.pop())
            shuffle(d)
            prepared_deck.extend(d)
        self.player_deck = prepared_deck

    def _add_neighbors_to_city_state(self):
        for con in CONNECTIONS:
            start, end = con[0], con[1]
            self.cities[start].add_neighbor(end)
            self.cities[end].add_neighbor(start)

    def get_cities(self) -> Dict[City, CityState]:
        return self.cities

    def get_city_state(self, city: City) -> CityState:
        return self.cities[city]

    def infection_rate(self) -> int:
        return INFECTIONS_RATES[self._infection_rate_marker]

    def report(self) -> str:
        min_cubes = min(self.cubes, key=self.cubes.get)
        return " ".join(
            [
                "active_player={active_player},",
                "player_deck_size={player_deck_size},",
                "infection_rate={infection_rate},",
                "outbreaks={outbreaks},",
                "min_cubes={min_cubes}",
            ]
        ).format(
            active_player="%s:%s" % (self.active_player.name.lower(), self.actions_left),
            player_deck_size=len(self._player_deck),
            infection_rate=self.infection_rate(),
            outbreaks=self.outbreaks,
            min_cubes="%s:%s" % (min_cubes.name, self.cubes[min_cubes]),
        )

    def _epidemic_1st_part(self):
        self._phase = Phase.EPIDEMIC
        self._infection_rate_marker += 1
        bottom_card = self.infection_deck.pop(-1)
        logging.info("Epidemic in %s!" % bottom_card)
        self._infect_city(bottom_card, times=3)
        self.infection_discard_pile.append(bottom_card)

    def epidemic_2nd_part(self):
        shuffle(self.infection_discard_pile)
        self.infection_deck = self.infection_discard_pile.copy() + self.infection_deck
        self.infection_discard_pile.clear()
        self.phase = Phase.DRAW_CARDS

    def draw_player_cards(self, count) -> List[Card]:
        drawn_cards: List[Card] = []
        for _ in itertools.repeat(None, count):
            drawn_cards.extend(self._draw_card())
        return drawn_cards

    def _draw_card(self) -> List[Card]:
        try:
            top_card = self.player_deck.pop(0)
            if isinstance(top_card, EpidemicCard):
                self._epidemic_1st_part()
                return []
            else:
                return [top_card]
        except IndexError:
            logging.info("you lost no more cards")
            self.game_state = GameState.LOST
            return []

    def draw_card(self) -> List[Card]:
        try:
            top_card = self.player_deck.pop(0)
            if isinstance(top_card, EpidemicCard):
                self._epidemic_1st_part()
                return []
            else:
                return [top_card]
        except IndexError:
            logging.info("you lost no more cards")
            self.game_state = GameState.LOST
            return []

    """
    Function to simulate outbreaks
    """

    def _outbreak(self, city: City, color: Virus, outbreaks: Set[City] = None):
        if outbreaks is None:
            outbreaks = set()
        if city not in outbreaks:
            self.outbreaks += 1
            if self.outbreaks > 7:
                self.game_state = GameState.LOST
            neighbors = self.get_city_state(city).get_neighbors()
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(city)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self, player_count: int):
        for player in self.players.values():
            player.add_cards(self.draw_player_cards(count=TOTAL_STARTING_PLAYER_CARDS - player_count))

    def get_player_current_city(self, player: Character) -> City:
        return self.players[player].get_city()

    def move_player_to_city(self, character: Character, city: City):
        if character == Character.MEDIC:
            [self.treat_city(city, color=c, times=3) for c, y in self.cures.items() if y]
        self.players[character].set_city(city)

    def play_card(self, player: Character, card: Card):
        if self.players[player].remove_card(card):
            self.player_discard_pile.append(card)
