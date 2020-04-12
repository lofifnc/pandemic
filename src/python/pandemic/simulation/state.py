import itertools
import logging
from random import shuffle, sample
from typing import List, Set, Optional

import numpy as np

from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.model.city_id import EventCard, EpidemicCard, Card
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.model.phases import ChooseCardsPhase, Phase
from pandemic.simulation.model.playerstate import PlayerState


class State:
    def __init__(self, player_count: int = PLAYER_COUNT):
        self.init(player_count)

    # noinspection PyAttributeOutsideInit
    # @profile
    def init(self, player_count: int):
        self.phase_state = None
        self.phase = Phase.SETUP
        # players
        self.players: Dict[Character, PlayerState] = {
            c: PlayerState() for c in sample(tuple(Character.__members__), k=player_count)
        }

        self.active_player: Character = list(self.players.keys())[0]

        # counters
        self.research_stations = 5
        self.outbreaks = 0
        self.infection_rate_marker = 0
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
        self.last_build_research_station = City.ATLANTA
        self.virus_to_cure = None

        # cards
        self.cities = create_cities_init_state()
        self.infection_deck: List[City] = list(self.cities.keys())
        shuffle(self.infection_deck)
        self.infection_discard_pile: List[City] = []

        self.player_deck: List[Card] = list(self.cities.keys()) + list(EventCard.__members__)
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

    def reset(self):
        self.init(len(self.players))

    def _init_infection_markers(self):
        [self.__draw_and_infect(i) for i in range(3, 0, -1)]

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self.infection_deck.pop(1)
            self.infect_city(top_card, times=num_infections)
            self.infection_discard_pile.append(top_card)

    def infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        outbreak = self._infect_city(city, color, times)
        if outbreak:
            self._outbreak(city, self.cities[city].color)
        return outbreak

    def _infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:

        outbreak_occurred = False
        city_state = self.cities[city]

        if color is None:
            color = city_state.color

        print(city_state.name, city_state.viral_state[color])

        if (
            self._is_city_protected_by_quarantine(city)
            or (self.cures[color]
            and (self.cubes[color] == COUNT_CUBES or self._character_location(Character.MEDIC) == city))
        ):
            # virus has been eradicated or city is protected by medic or quarantine expert
            return outbreak_occurred
        for _ in itertools.repeat(None, times):
            outbreak_occurred = self.cities[city].inc_infection(color)
            if outbreak_occurred:
                break

            if self.cubes[color] > 0:
                self.cubes[color] -= 1
            else:
                self.game_state = GameState.LOST

        return outbreak_occurred

    def _character_location(self, char: Character) -> Optional[City]:
        state = self.players.get(char, None)
        return state.city if state else None

    def start_choose_cards_phase(self, inp: ChooseCardsPhase):
        self.phase = Phase.CHOOSE_CARDS
        self.phase_state = inp

    def _is_city_protected_by_quarantine(self, city) -> bool:
        if self.phase != Phase.SETUP and Character.QUARANTINE_SPECIALIST in self.players.keys():
            location = self._character_location(Character.QUARANTINE_SPECIALIST)
            return city in self.cities[location].neighbors.union([location])
        return False

    def treat_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        city_state = self.cities[city]
        if color is None:
            color = city_state.color

        for _ in itertools.repeat(None, 3 if self.cures[color] else times):
            is_empty = self.cities[city].dec_infection(color)
            if is_empty:
                break
            self.cubes[color] += 1

        return is_empty

    def draw_cards(self, action: ActionInterface):
        if self.drawn_cards < 2:
            self.players[self.active_player].add_card(self.draw_card())
            self.drawn_cards += 1
        if self.drawn_cards == 2:
            self.drawn_cards = 0
            self.phase = Phase.INFECTIONS

    def infections(self, action: ActionInterface):
        if self.infections_steps == 0 and self.one_quiet_night:
            pass
        elif self.infections_steps < self.infection_rate():
            try:
                top_card = self.infection_deck.pop(0)
            except IndexError:
                # TODO: inspect here!
                self.game_state = GameState.LOST
                return
            self.infect_city(top_card)

            self.infection_discard_pile.append(top_card)
            self.infections_steps += 1
        if self.infections_steps == self.infection_rate() or self.one_quiet_night:
            self.infections_steps = 0
            if self.infections_steps == 0:
                self.one_quiet_night = False
            [ps.signal_turn_end() for ps in self.players.values()]
            self.active_player = self.get_next_player()
            self.phase = Phase.ACTIONS

    def get_next_player(self) -> Character:
        list_of_player_colors = list(self.players.keys())
        index_of_active_player = list_of_player_colors.index(self.active_player)
        return list_of_player_colors[(index_of_active_player + 1) % len(list_of_player_colors)]

    def _prepare_player_deck(self):
        prepared_deck: List[Card] = []
        city_cards = self.player_deck
        shuffle(city_cards)
        chunks = np.array_split(city_cards, EPIDEMIC_CARDS)
        epidemic_cards = list(EpidemicCard.__members__)
        [self.__prepare_chunk(c, epidemic_cards, prepared_deck) for c in chunks]
        self.player_deck = prepared_deck

    @staticmethod
    def __prepare_chunk(c, epidemic_cards, prepared_deck):
        d = list(c)
        d.append(epidemic_cards.pop())
        shuffle(d)
        prepared_deck.extend(d)

    def _add_neighbors_to_city_state(self):
        [self.__resolve_connection(con) for con in CONNECTIONS]

    def __resolve_connection(self, con):
        start, end = con[0], con[1]
        self.cities[start].add_neighbor(end)
        self.cities[end].add_neighbor(start)

    def infection_rate(self) -> int:
        return INFECTIONS_RATES[self.infection_rate_marker]

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
            active_player="%s:%s" % (self.active_player, self.actions_left),
            player_deck_size=len(self.player_deck),
            infection_rate=self.infection_rate(),
            outbreaks=self.outbreaks,
            min_cubes="%s:%s" % (min_cubes, self.cubes[min_cubes]),
        )

    def _epidemic_1st_part(self):
        self.phase = Phase.EPIDEMIC
        self.infection_rate_marker += 1
        bottom_card = self.infection_deck.pop(-1)
        print("epidemic!!!")
        logging.info("Epidemic in %s!" % bottom_card)
        self.infect_city(bottom_card, times=3)
        self.infection_discard_pile.append(bottom_card)

    def epidemic_2nd_part(self):
        shuffle(self.infection_discard_pile)
        self.infection_deck = self.infection_discard_pile.copy() + self.infection_deck
        self.infection_discard_pile.clear()
        self.phase = Phase.DRAW_CARDS

    def draw_player_cards(self, count) -> List[Card]:
        drawn_cards: List[Card] = []
        for _ in itertools.repeat(None, count):
            drawn_cards.append(self.draw_card())
        return drawn_cards

    def draw_card(self) -> Optional[Card]:
        try:
            top_card = self.player_deck.pop(0)
            if Card.card_type(top_card) == Card.EPIDEMIC:
                self._epidemic_1st_part()
                return -1
            else:
                return top_card
        except IndexError:
            logging.info("you lost no more cards")
            self.game_state = GameState.LOST
            return -1

    """
    Function to simulate outbreaks
    """

    def _outbreak(self, city: City, color: Virus, outbreaks: Set[City] = None):
        print("outbreak")
        if outbreaks is None:
            outbreaks = set()
        if city not in outbreaks:
            self.outbreaks += 1
            if self.outbreaks > 7:
                self.game_state = GameState.LOST
            neighbors = self.cities[city].neighbors
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(city)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self, player_count: int):
        [
            player.add_cards(self.draw_player_cards(count=TOTAL_STARTING_PLAYER_CARDS - player_count))
            for player in self.players.values()
        ]

    def get_player_current_city(self, player: Character) -> City:
        return self.players[player].city

    def move_player_to_city(self, character: Character, city: City):
        if character == Character.MEDIC:
            [self.treat_city(city, color=c, times=3) for c, y in self.cures.items() if y]
        self.players[character].city = city

    def play_card(self, player: Character, card: Card):
        if self.players[player].remove_card(card):
            self.player_discard_pile.append(card)
