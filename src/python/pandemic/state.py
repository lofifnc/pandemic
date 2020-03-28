import itertools
import logging
from collections import Counter
from enum import Enum
from random import shuffle, choices
from typing import List, Set, Optional

import numpy as np

from pandemic.model.actions import (
    ActionInterface,
    Movement,
    Other,
    Event,
    ThrowCard,
    DiscoverCure,
    BuildResearchStation,
    TreatDisease,
    ShareKnowledge,
    ReserveCard,
    ResilientPopulation,
    Airlift,
    Forecast,
    GovernmentGrant,
    OneQuietNight,
    DriveFerry,
    DirectFlight,
    CharterFlight,
    ShuttleFlight,
    Dispatch,
    OperationsFlight,
)
from pandemic.model.city_id import EventCard, EpidemicCard, Card
from pandemic.model.constants import *
from pandemic.model.enums import Character, GameState
from pandemic.model.playerstate import PlayerState
from itertools import chain


class Phase(Enum):
    SETUP = 0
    ACTIONS = 1
    DRAW_CARDS = 2
    INFECTIONS = 3
    EPIDEMIC = 4


class State:

    def __init__(self, player_count: int = PLAYER_COUNT):
        self._phase = Phase.SETUP
        # players
        self._players: Dict[Character, PlayerState] = {
            c: PlayerState() for c in choices(list(Character.__members__.values()), k=player_count)
        }

        self._active_player: Character = list(self._players.keys())[0]

        # counters
        self._research_stations = 5
        self._outbreaks = 0
        self._infection_rate_marker = 0
        self._cubes = {
            Virus.YELLOW: COUNT_CUBES,
            Virus.BLACK: COUNT_CUBES,
            Virus.BLUE: COUNT_CUBES,
            Virus.RED: COUNT_CUBES,
        }
        self._player_actions = PLAYER_ACTIONS
        self._cures: Dict[Virus, bool] = {Virus.YELLOW: False, Virus.BLACK: False, Virus.BLUE: False, Virus.RED: False}
        self._one_quiet_night = False
        # phase specific state
        self._drawn_cards = 0
        self._infections = 0

        # cards
        self._cities = create_cities_init_state()
        self._infection_deck: List[City] = list(self._cities.keys())
        shuffle(self._infection_deck)
        self._infection_discard_pile: List[City] = []

        self._player_deck: List[Card] = list(self._cities.keys()) + list(EventCard.__members__.values())
        shuffle(self._player_deck)
        self._serve_player_cards(player_count)
        self._prepare_player_deck()
        self._player_discard_pile: List[Card] = []

        self._add_neighbors_to_city_state()
        self._game_state = GameState.RUNNING

        # infection
        self._init_infection_markers()
        self._phase = Phase.ACTIONS

    def _init_infection_markers(self):
        for i in range(3, 0, -1):
            self.__draw_and_infect(i)

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self._infection_deck.pop(1)
            self._infect_city(top_card, times=num_infections)
            self._infection_discard_pile.append(top_card)

    def _character_location(self, char: Character) -> Optional[City]:
        state = self._players.get(char, None)
        return state.get_city() if state else None

    def _is_city_protected_by_quarantine(self, city) -> bool:
        if self._phase != Phase.SETUP and Character.QUARANTINE_SPECIALIST in self._players.keys():
            location = self._character_location(Character.QUARANTINE_SPECIALIST)
            return city in self.get_neighbors(location).union([location])
        return False

    def _infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:

        outbreak_occurred = False
        city_state = self.get_city_state(city)
        if color is None:
            color = city_state.get_color()

        if (
            self._is_city_protected_by_quarantine(city)
            or self._cures[color]
            and (self._cubes[color] == COUNT_CUBES or self._character_location(Character.MEDIC) == city)
        ):
            # virus has been eradicated or city is protected by medic or quarantine expert
            return outbreak_occurred
        for _ in itertools.repeat(None, times):
            outbreak_occurred = self.get_city_state(city).inc_infection(color)
            if outbreak_occurred:
                break

            if self._cubes[color] > 0:
                self._cubes[color] -= 1
            else:
                self._game_state = GameState.LOST

        return outbreak_occurred

    def _treat_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        city_state = self.get_city_state(city)
        if color is None:
            color = city_state.get_color()

        for _ in itertools.repeat(None, 3 if self._cures[color] else times):
            is_empty = self.get_city_state(city).dec_infection(color)
            if is_empty:
                break
            self._cubes[color] += 1

        return is_empty

    def step(self, action: ActionInterface) -> Set[ActionInterface]:

        if isinstance(action, ThrowCard):
            self.throw_card_action(action)
        elif isinstance(action, Event):
            self.event_action(action)
        if self._phase == Phase.ACTIONS and not isinstance(action, Event):
            self.actions(action)
        elif self._phase == Phase.DRAW_CARDS:
            self.draw_cards(action)
        elif self._phase == Phase.INFECTIONS:
            self.infections(action)
        elif self._phase == Phase.EPIDEMIC:
            self._epidemic_2nd_part()

        return self.get_possible_actions()

    def actions(self, action: ActionInterface):
        if self._player_actions > 0:
            if isinstance(action, Movement):
                self.move_player(action)
            elif isinstance(action, Other):
                self.other_action(action)
            if all(value for value in self._cures.values()):
                self._game_state = GameState.WIN
            self._player_actions -= 1
        if self._player_actions == 0:
            self._player_actions = PLAYER_ACTIONS
            self._phase = Phase.DRAW_CARDS

    def draw_cards(self, action: ActionInterface):
        if self._drawn_cards < 2:
            self.active_player().add_cards(self.draw_card())
            self._drawn_cards += 1
        if self._drawn_cards == 2:
            self._drawn_cards = 0
            self._phase = Phase.INFECTIONS

    def infections(self, action: ActionInterface):
        if self._infections == 0 and self._one_quiet_night:
            pass
        elif self._infections < self.infection_rate():
            top_card = self._infection_deck.pop(0)
            outbreak = self._infect_city(top_card)
            if outbreak:
                self._outbreak(top_card, self.get_city_state(top_card).get_color())
            self._infection_discard_pile.append(top_card)
            self._infections += 1
        if self._infections == self.infection_rate() or self._one_quiet_night:
            self._infections = 0
            if self._infections == 0:
                self._one_quiet_night = False
            [ps.signal_turn_end() for ps in self._players.values()]
            self._active_player = self.get_next_player()
            self._phase = Phase.ACTIONS

        return self.get_possible_actions()

    def active_player(self) -> PlayerState:
        return self._players[self._active_player]

    def get_next_player(self) -> Character:
        list_of_player_colors = list(self._players.keys())
        index_of_active_player = list_of_player_colors.index(self._active_player)
        return list_of_player_colors[(index_of_active_player + 1) % len(list_of_player_colors)]

    def get_possible_actions(self, player: Character = None) -> Set[ActionInterface]:
        if player is None:
            player = self._active_player

        possible_actions: Set[ActionInterface] = self.get_possible_event_actions()

        # check all players for hand limit and prompt action
        too_many_cards = False
        for color, state in self.get_players().items():
            if state.num_cards() > 7:
                too_many_cards = True
                possible_actions = possible_actions.union(ThrowCard(color, c) for c in state.get_cards())

        if too_many_cards:
            return possible_actions

        if self._phase == Phase.ACTIONS:
            possible_actions = possible_actions.union(self.get_possible_move_actions(player)).union(
                self.get_possible_other_actions(player)
            )
        if self._phase == Phase.DRAW_CARDS:
            return possible_actions
        if self._phase == Phase.INFECTIONS:
            return possible_actions
        return possible_actions

    def get_neighbors(self, city: City) -> Set[City]:
        return self.get_city_state(city).get_neighbors()

    def _prepare_player_deck(self):
        prepared_deck: List[Card] = []
        city_cards = self._player_deck
        shuffle(city_cards)
        chunks = np.array_split(city_cards, EPIDEMIC_CARDS)
        epidemic_cards = set(EpidemicCard.__members__.values())
        for c in chunks:
            d = list(c)
            d.append(epidemic_cards.pop())
            shuffle(d)
            prepared_deck.extend(d)
        self._player_deck = prepared_deck

    def _add_neighbors_to_city_state(self):
        for con in CONNECTIONS:
            start, end = con[0], con[1]
            self._cities[start].add_neighbor(end)
            self._cities[end].add_neighbor(start)

    def get_cities(self) -> Dict[City, CityState]:
        return self._cities

    def get_city_state(self, city: City) -> CityState:
        return self._cities[city]

    def infection_rate(self) -> int:
        return INFECTIONS_RATES[self._infection_rate_marker]

    def report(self) -> str:
        min_cubes = min(self._cubes, key=self._cubes.get)
        return " ".join(
            [
                "active_player={active_player},",
                "player_deck_size={player_deck_size},",
                "infection_rate={infection_rate},",
                "outbreaks={outbreaks},",
                "min_cubes={min_cubes}",
            ]
        ).format(
            active_player="%s:%s" % (self._active_player.name.lower(), self._player_actions),
            player_deck_size=len(self._player_deck),
            infection_rate=self.infection_rate(),
            outbreaks=self._outbreaks,
            min_cubes="%s:%s" % (min_cubes.name, self._cubes[min_cubes]),
        )

    def _epidemic_1st_part(self):
        self._phase = Phase.EPIDEMIC
        self._infection_rate_marker += 1
        bottom_card = self._infection_deck.pop(-1)
        logging.info("Epidemic in %s!" % bottom_card)
        self._infect_city(bottom_card, times=3)
        self._infection_discard_pile.append(bottom_card)

    def _epidemic_2nd_part(self):
        shuffle(self._infection_discard_pile)
        self._infection_deck = self._infection_discard_pile.copy() + self._infection_deck
        self._infection_discard_pile.clear()
        self._phase = Phase.DRAW_CARDS

    def draw_player_cards(self, count) -> List[Card]:
        drawn_cards: List[Card] = []
        for _ in itertools.repeat(None, count):
            drawn_cards.extend(self.draw_card())
        return drawn_cards

    def draw_card(self) -> List[Card]:
        try:
            top_card = self._player_deck.pop(0)
            if isinstance(top_card, EpidemicCard):
                self._epidemic_1st_part()
                return []
            else:
                return [top_card]
        except IndexError:
            logging.info("you lost no more cards")
            self._game_state = GameState.LOST
            return []

    def get_player_cards(self, player: Character = None):
        if player is None:
            player = self._active_player
        return self._players[player].get_cards()

    def player_cards_to_string(self, player: Character = None) -> str:
        return " ".join(map(lambda x: x.name.lower(), self.get_player_cards(player)))

    def get_actions_left(self):
        return self._player_actions

    """
    Function to simulate outbreaks
    """

    def _outbreak(self, city: City, color: Virus, outbreaks: Set[City] = None):
        if outbreaks is None:
            outbreaks = set()
        if city not in outbreaks:
            self._outbreaks += 1
            if self._outbreaks > 7:
                self._game_state = GameState.LOST
            neighbors = self.get_city_state(city).get_neighbors()
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(city)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self, player_count: int):
        for player in self._players.values():
            player.add_cards(self.draw_player_cards(count=TOTAL_STARTING_PLAYER_CARDS - player_count))

    def move_player(self, move: Movement):
        destination_city = move.destination
        character = move.player

        if isinstance(move, DriveFerry):
            assert destination_city in self.get_city_state(self.get_player_current_city(character)).get_neighbors()
        if isinstance(move, DirectFlight):
            self._player_play_card(character, destination_city)
        if isinstance(move, CharterFlight):
            self._player_play_card(character, self.get_player_current_city(character))
        if isinstance(move, ShuttleFlight):
            assert (
                self.get_city_state(self.get_player_current_city(character)).has_research_station()
                and self.get_city_state(destination_city).has_research_station()
            )
        if isinstance(move, OperationsFlight):
            self._player_play_card(character, move.discard_card)
            self._players[character].used_operations_expert_shuttle_move()

        self.__move_player_to_city(character, destination_city)

    def get_players(self) -> Dict[Character, PlayerState]:
        return self._players

    def get_phase(self) -> Phase:
        return self._phase

    def get_player_current_city(self, player: Character) -> City:
        return self._players[player].get_city()

    def other_action(self, action: Other, character: Character = None):
        if character is None:
            character = self._active_player

        if isinstance(action, TreatDisease):
            self._treat_city(action.city, action.target_virus, times=1 if character != Character.MEDIC else 3)
        elif isinstance(action, BuildResearchStation):
            if character != Character.OPERATIONS_EXPERT:
                self._player_play_card(character, action.city)
            self.get_city_state(action.city).build_research_station()
            if action.move_from:
                self._cities[action.move_from].remove_research_station()
            else:
                self._research_stations -= 1
        elif isinstance(action, DiscoverCure):
            for card in action.card_combination:
                self._player_play_card(character, card)
            self._cures[action.target_virus] = True
            medic = self._players.get(Character.MEDIC, None)
            if medic:
                self._treat_city(medic.get_city(), action.target_virus, 3)
        elif isinstance(action, ShareKnowledge):
            self._player_play_card(action.player, action.card)
            self._players[action.target_player].add_card(action.card)
        elif isinstance(action, ReserveCard):
            self._player_discard_pile.remove(action.card)
            self._players[character].set_contingency_planner_card(action.card)

    def get_possible_move_actions(self, character: Character = None) -> Set[Movement]:

        if character is None:
            character = self._active_player

        player_state = self._players[character]

        moves = self.__possible_moves(character, player_state.get_city_cards())

        # Dispatcher
        if character == Character.DISPATCHER:
            for c in self._players.keys():
                moves = moves.union(self.__possible_moves(c, player_state.get_city_cards()))
            for f, t in itertools.permutations(self._players.keys(), 2):
                moves.add(Dispatch(f, self.get_player_current_city(t)))

            self._players.keys()

        return moves

    def __possible_moves(self, character: Character, city_cards: Set[City]) -> Set[Movement]:
        player_state = self._players[character]
        current_city = player_state.get_city()
        # drives / ferries
        moves: Set[Movement] = set(map(lambda c: DriveFerry(character, c), self.get_neighbors(current_city)))

        # direct flights
        direct_flights = set(DirectFlight(character, c) for c in city_cards if c != current_city)

        # charter flights
        charter_flights = set(
            CharterFlight(character, c)
            for c in (self._cities.keys() if current_city in city_cards else [])
            if c != current_city
        )
        # shuttle flights between two cities with research station
        shuttle_flights: Set[Movement] = set()
        if self.get_city_state(current_city).has_research_station():
            shuttle_flights = set(
                ShuttleFlight(character, cid)
                for cid, loc in self.get_cities().items()
                if loc.has_research_station() and cid != current_city
            )

        # operations expert charter flights
        operation_flights: Set[Movement] = set()
        if (
            self._active_player == Character.OPERATIONS_EXPERT
            and self.get_city_state(current_city).has_research_station()
            and player_state.operations_expert_has_charter_flight()
        ):
            for card in player_state.get_city_cards():
                operation_flights = operation_flights.union(
                    {
                        OperationsFlight(character, destination=c, discard_card=card)
                        for c in self._cities.keys()
                        if c != current_city
                    }
                )

        return moves.union(direct_flights).union(charter_flights).union(shuttle_flights).union(operation_flights)

    def get_city_color(self, city: City) -> Virus:
        return self.get_city_state(city).get_color()

    def get_game_condition(self) -> GameState:
        return self._game_state

    def get_possible_other_actions(self, character: Character = None) -> Set[ActionInterface]:
        if character is None:
            character = self._active_player
        else:
            character = character

        player = self._players[character]

        current_city = player.get_city()
        possible_actions: Set[ActionInterface] = set()

        # What is treatable?
        for virus, count in self.get_city_state(current_city).get_viral_state().items():
            if count > 0:
                possible_actions.add(TreatDisease(current_city, target_virus=virus))

        # Can I build research station?
        if (
            not self._cities[current_city].has_research_station()
            and current_city in player.get_cards()
            or character == Character.OPERATIONS_EXPERT
        ):
            possible_actions = possible_actions.union(
                {
                    BuildResearchStation(current_city, move_from=c)
                    for c, s in self._cities.items()
                    if s.has_research_station()
                }
                if self._research_stations == 0
                else {BuildResearchStation(current_city)}
            )

        # Can I discover a cure at this situation?
        if self.get_city_state(current_city).has_research_station():
            player_card_viruses = [self.get_city_color(card) for card in player.get_cards() if isinstance(card, City)]
            for virus, count in Counter(player_card_viruses).items():
                cards_for_cure = 4 if character == Character.SCIENTIST else 5
                if count >= cards_for_cure and not self._cures[virus]:
                    potential_cure_cards: List[City] = list(
                        filter(lambda c: self.get_city_color(c) == virus, player.get_city_cards())
                    )

                    for cure_cards in list(itertools.combinations(potential_cure_cards, cards_for_cure)):
                        possible_actions.add(DiscoverCure(target_virus=virus, card_combination=frozenset(cure_cards)))

        # Can I share knowledge?
        players_in_city: Dict[Character, PlayerState] = {
            c: p for c, p in self._players.items() if p.get_city() == current_city
        }
        if len(players_in_city) > 1:
            possible_actions = possible_actions.union(
                self.__check_oldschool_knowledge_sharing(character, players_in_city)
            )
            # Researcher
            researcher = players_in_city.get(Character.RESEARCHER, {})
            for card in researcher and researcher.get_city_cards():
                possible_actions = possible_actions.union(
                    ShareKnowledge(Character.RESEARCHER, card, target_player=other)
                    for other in players_in_city.keys()
                    if other != character.RESEARCHER
                )

        # Contigency Planner
        if character == Character.CONTINGENCY_PLANNER and not self._players[character].get_contingency_planner_card():
            for card in self._player_discard_pile:
                possible_actions.add(ReserveCard(card))

        return possible_actions

    def __check_oldschool_knowledge_sharing(
        self, character: Character, players_in_city: Dict[Character, PlayerState]
    ) -> Set[ActionInterface]:
        possible_actions: Set[ActionInterface] = set()
        current_city = self.get_player_current_city(character)
        for c, ps in filter(lambda pst: current_city in pst[1].get_cards(), players_in_city.items()):
            if c == character:
                # give card to other player
                share_with_others = set(
                    ShareKnowledge(card=current_city, player=character, target_player=other)
                    for other in players_in_city.keys()
                    if other != character
                )
                possible_actions = possible_actions.union(share_with_others)
            else:
                # get card from other player
                possible_actions.add(ShareKnowledge(card=current_city, player=c, target_player=character))
        return possible_actions

    def event_action(self, event: Event):
        if isinstance(event, Forecast):
            self._infection_deck[:6] = event.forecast
            self._player_play_card(event.player, EventCard.FORECAST)
        elif isinstance(event, GovernmentGrant):
            self.get_city_state(event.target_city).build_research_station()
            self._player_play_card(event.player, EventCard.GOVERNMENT_GRANT)
        elif isinstance(event, Airlift):
            self.__move_player_to_city(event.target_player, event.destination)
            self._player_play_card(event.player, EventCard.AIRLIFT)
        elif isinstance(event, ResilientPopulation):
            self._infection_discard_pile.remove(event.discard_city)
            self._player_play_card(event.player, EventCard.RESILIENT_POPULATION)
        elif isinstance(event, OneQuietNight):
            self._one_quiet_night = True
            self._player_play_card(event.player, EventCard.ONE_QUIET_NIGHT)

    def __move_player_to_city(self, character: Character, city: City):
        if character == Character.MEDIC:
            [self._treat_city(city, color=c, times=3) for c, y in self._cures.items() if y]
        self._players[character].set_city(city)

    def _player_play_card(self, player: Character, card: Card):
        if self._players[player].remove_card(card):
            self._player_discard_pile.append(card)

    def get_possible_event_actions(self) -> Set[Event]:
        possible_actions: Set[Event] = set()
        players_with_event_cards = filter(
            lambda t: t[2], [(p, s, s.get_event_cards()) for p, s in self.get_players().items()]
        )
        for player, state, event_cards in players_with_event_cards:
            possible_actions = possible_actions.union(
                chain.from_iterable(self.__action_for_event_card(player, state, card) for card in event_cards)
            )

        return possible_actions

    def __action_for_event_card(self, player_color: Character, state: PlayerState, event_card: EventCard) -> Set[Event]:

        possible_actions: Set[Event] = set()
        if event_card == EventCard.RESILIENT_POPULATION:
            for card in self._infection_discard_pile:
                possible_actions.add(ResilientPopulation(player=player_color, discard_city=card))

        if event_card == EventCard.AIRLIFT:
            for city in self.get_cities().keys():
                for p, _ in filter(lambda pcp: pcp[1].get_city() != city, self.get_players().items()):
                    possible_actions.add(Airlift(player=player_color, target_player=p, destination=city))

        if event_card == EventCard.FORECAST:
            for permutation in itertools.permutations(self._infection_deck[:6]):
                possible_actions.add(Forecast(player=player_color, forecast=tuple(permutation)))

        if event_card == EventCard.GOVERNMENT_GRANT and self._research_stations > 0:
            for city, _ in filter(lambda cid: not cid[1].has_research_station(), self.get_cities().items()):
                possible_actions.add(GovernmentGrant(player=player_color, target_city=city))

        if event_card == EventCard.ONE_QUIET_NIGHT:
            possible_actions.add(OneQuietNight(player=player_color))

        return possible_actions

    def throw_card_action(self, action: ThrowCard):
        assert isinstance(action, ThrowCard)
        self._players[action.player].remove_card(action.card)
