import itertools
import logging
import random
from typing import List, Optional, Tuple, Any

import numpy as np

from pandemic.simulation.model.actions import ActionInterface
from pandemic.simulation.model.city_id import EventCard, EpidemicCard, Card
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.model.phases import ChooseCardsPhase, Phase
from pandemic.simulation.model.playerstate import PlayerState


@dataclass
class InternalState:

    phase_state: Any
    previous_phase: int
    phase: int
    # players
    players: Dict[Character, PlayerState]

    active_player: int

    research_stations: int
    outbreaks: int
    infection_rate_marker: int
    cubes: Dict[int, int]

    actions_left: int
    cures: Dict[int, bool]
    one_quiet_night: bool

    # phase specific state
    drawn_cards: int
    infections_steps: int
    last_build_research_station: int
    virus_to_cure: Optional[int]

    # cards
    cities: Dict[int, CityState]
    infection_deck: List[int]
    infection_discard_pile: List[City]

    player_deck: List[Card]
    player_discard_pile: List[Card]

    game_state: int


class State:
    def __init__(
        self,
        num_epidemic_cards=5,
        player_count: int = PLAYER_COUNT,
        characters: Tuple[int] = tuple(),
        player_deck_shuffle_seed=None,
        infect_deck_shuffle_seed=None,
        epidemic_shuffle_seed=None,
    ):
        self.epidemic_shuffle_seed = epidemic_shuffle_seed
        self.infect_deck_shuffle_seed = infect_deck_shuffle_seed
        self.num_epidemic_cards = num_epidemic_cards
        self.player_deck_shuffle_seed = player_deck_shuffle_seed
        self.random = random.Random()
        # TODO: allow for new player shuffle on reset:
        self.characters = characters if characters else random.sample(tuple(Character.__members__), k=player_count)
        self.internal_state: InternalState = None
        self.init()

    # @profile
    def init(self):

        players = {c: PlayerState() for c in self.characters}

        infection_deck: List[City] = list(city_colors.keys())

        if self.infect_deck_shuffle_seed is not None:
            self.random.seed(self.infect_deck_shuffle_seed)
        self.random.shuffle(infection_deck)

        if self.infect_deck_shuffle_seed is not None:
            self.random.seed(self.infect_deck_shuffle_seed)

        player_deck: List[Card] = list(city_colors.keys()) + list(EventCard.__members__)
        self.random.shuffle(player_deck)

        self.internal_state = InternalState(
            players=players,
            active_player=list(players.keys())[0],
            research_stations=5,
            outbreaks=0,
            infection_rate_marker=0,
            cubes={
                Virus.YELLOW: COUNT_CUBES,
                Virus.BLACK: COUNT_CUBES,
                Virus.BLUE: COUNT_CUBES,
                Virus.RED: COUNT_CUBES,
            },
            actions_left=PLAYER_ACTIONS,
            cures={Virus.YELLOW: False, Virus.BLACK: False, Virus.BLUE: False, Virus.RED: False},
            one_quiet_night=False,
            drawn_cards=0,
            infections_steps=0,
            last_build_research_station=City.ATLANTA,
            virus_to_cure=None,
            cities=create_cities_init_state(),
            infection_deck=infection_deck,
            infection_discard_pile=[],
            player_deck=player_deck,
            player_discard_pile=[],
            previous_phase=Phase.SETUP,
            phase=Phase.ACTIONS,
            game_state=GameState.RUNNING,
            phase_state=None,
        )

        self._serve_player_cards(len(self.characters))
        self._prepare_player_deck(self.num_epidemic_cards)

        # infection init
        self._init_infection_markers()

        if self.epidemic_shuffle_seed is not None:
            self.random.seed(self.epidemic_shuffle_seed)

    def reset(self):
        self.init()

    def _init_infection_markers(self):
        [self.__draw_and_infect(i) for i in range(3, 0, -1)]

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self.infection_deck.pop(1)
            self.infect_city(top_card, times=num_infections)
            self.infection_discard_pile.append(top_card)

    def infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        if color is None:
            color = CITY_DATA[city].color
        outbreak = self._infect_city(city, color, times)
        if outbreak:
            self._outbreak(city, color)
        return outbreak

    def _infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:

        outbreak_occurred = False

        if color is None:
            color = CITY_DATA[city].color

        if self._is_city_protected_by_quarantine(city) or (
            self.cures[color]
            and (self.cubes[color] == COUNT_CUBES or self._character_location(Character.MEDIC) == city)
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
            return city in CITY_DATA[location].neighbors.union([location])
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
            if self.phase != Phase.EPIDEMIC:
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

    def _prepare_player_deck(self, num_epidemic_cards):
        prepared_deck: List[Card] = []
        city_cards = self.player_deck
        self.random.shuffle(city_cards)
        chunks = np.array_split(city_cards, num_epidemic_cards)
        epidemic_cards = list(EpidemicCard.__members__)
        [self.__prepare_chunk(c, epidemic_cards, prepared_deck) for c in chunks]
        self.player_deck = prepared_deck

    def __prepare_chunk(self, c, epidemic_cards, prepared_deck):
        d = list(c)
        d.append(epidemic_cards.pop())
        self.random.shuffle(d)
        prepared_deck.extend(d)

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
        logging.info("Epidemic in %s!" % bottom_card)
        self.infect_city(bottom_card, times=3)
        self.infection_discard_pile.append(bottom_card)

    def epidemic_2nd_part(self):
        self.random.shuffle(self.infection_discard_pile)
        self.infection_deck = self.infection_discard_pile.copy() + self.infection_deck
        self.infection_discard_pile.clear()
        if self.drawn_cards == 2:
            self.drawn_cards = 0
            self.phase = Phase.INFECTIONS
        else:
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
        if outbreaks is None:
            outbreaks = set()
        if city not in outbreaks:
            self.outbreaks += 1
            if self.outbreaks > 7:
                self.game_state = GameState.LOST
                return
            neighbors = CITY_DATA[city].neighbors
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

    @property
    def phase_state(self):
        return self.internal_state.phase_state

    @phase_state.setter
    def phase_state(self, value):
        self.internal_state.phase_state = value

    @property
    def previous_phase(self):
        return self.internal_state.previous_phase

    @previous_phase.setter
    def previous_phase(self, value):
        self.internal_state.previous_phase = value

    @property
    def phase(self):
        return self.internal_state.phase

    @phase.setter
    def phase(self, value):
        self.internal_state.phase = value

    @property
    def players(self):
        return self.internal_state.players

    @players.setter
    def players(self, value):
        self.internal_state.players = value

    @property
    def active_player(self):
        return self.internal_state.active_player

    @active_player.setter
    def active_player(self, value):
        self.internal_state.active_player = value

    @property
    def research_stations(self):
        return self.internal_state.research_stations

    @research_stations.setter
    def research_stations(self, value):
        self.internal_state.research_stations = value

    @property
    def outbreaks(self):
        return self.internal_state.outbreaks

    @outbreaks.setter
    def outbreaks(self, value):
        self.internal_state.outbreaks = value

    @property
    def infection_rate_marker(self):
        return self.internal_state.infection_rate_marker

    @infection_rate_marker.setter
    def infection_rate_marker(self, value):
        self.internal_state.infection_rate_marker = value

    @property
    def cubes(self):
        return self.internal_state.cubes

    @cubes.setter
    def cubes(self, value):
        self.internal_state.cubes = value

    @property
    def actions_left(self):
        return self.internal_state.actions_left

    @actions_left.setter
    def actions_left(self, value):
        self.internal_state.actions_left = value

    @property
    def cures(self):
        return self.internal_state.cures

    @cures.setter
    def cures(self, value):
        self.internal_state.cures = value

    @property
    def one_quiet_night(self):
        return self.internal_state.one_quiet_night

    @one_quiet_night.setter
    def one_quiet_night(self, value):
        self.internal_state.one_quiet_night = value

    @property
    def drawn_cards(self):
        return self.internal_state.drawn_cards

    @drawn_cards.setter
    def drawn_cards(self, value):
        self.internal_state.drawn_cards = value

    @property
    def infections_steps(self):
        return self.internal_state.infections_steps

    @infections_steps.setter
    def infections_steps(self, value):
        self.internal_state.infections_steps = value

    @property
    def last_build_research_station(self):
        return self.internal_state.last_build_research_station

    @last_build_research_station.setter
    def last_build_research_station(self, value):
        self.internal_state.last_build_research_station = value

    @property
    def virus_to_cure(self):
        return self.internal_state.virus_to_cure

    @virus_to_cure.setter
    def virus_to_cure(self, value):
        self.internal_state.virus_to_cure = value

    @property
    def cities(self):
        return self.internal_state.cities

    @cities.setter
    def cities(self, value):
        self.internal_state.cities = value

    @property
    def infection_deck(self):
        return self.internal_state.infection_deck

    @infection_deck.setter
    def infection_deck(self, value):
        self.internal_state.infection_deck = value

    @property
    def infection_discard_pile(self):
        return self.internal_state.infection_discard_pile

    @infection_discard_pile.setter
    def infection_discard_pile(self, value):
        self.internal_state.infection_discard_pile = value

    @property
    def player_deck(self):
        return self.internal_state.player_deck

    @player_deck.setter
    def player_deck(self, value):
        self.internal_state.player_deck = value

    @property
    def player_discard_pile(self):
        return self.internal_state.player_discard_pile

    @player_discard_pile.setter
    def player_discard_pile(self, value):
        self.internal_state.player_discard_pile = value

    @property
    def game_state(self):
        return self.internal_state.game_state

    @game_state.setter
    def game_state(self, value):
        self.internal_state.game_state = value
