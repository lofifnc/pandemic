import itertools
import logging
from collections import Counter
from enum import Enum
from random import shuffle
from typing import List, Set

import numpy as np

from pandemic.model.actions import ActionInterface, Movement, Other, Event, ThrowCard
from pandemic.model.city_id import EventCard, EpidemicCard, Card
from pandemic.model.constants import *
from pandemic.model.enums import PlayerColor, MovementAction, OtherAction, GameState
from pandemic.model.playerstate import PlayerState


class Phase(Enum):
    ACTIONS = 1
    DRAW_CARDS = 2
    INFECTIONS = 3
    EPIDEMIC = 4


class State:
    def __init__(self, player_count: int = PLAYER_COUNT):

        # players
        self._players: Dict[PlayerColor, PlayerState] = {
            PlayerColor(n): PlayerState() for n in range(1, player_count + 1)
        }

        self._active_player: PlayerColor = list(self._players.keys())[0]

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
        self._phase = Phase.ACTIONS
        self._resilient = False
        # phase specific state
        self._drawn_cards = 0
        self._infections = 0

        # cards
        self._infection_deck: List[City] = list(CITIES.keys())
        shuffle(self._infection_deck)
        self._infection_discard_pile: List[City] = []

        self._player_deck: List[Card] = list(CITIES.keys()) + list(EventCard.__members__.values())
        shuffle(self._player_deck)
        self._serve_player_cards(player_count)
        self._prepare_player_deck()
        self._player_discard_pile: List[Card] = []

        self._cities = CITIES.copy()
        self._add_neighbors_to_city_state()
        self._game_state = GameState.RUNNING

        # infection
        self._init_infection_markers()

    def _init_infection_markers(self):
        for i in range(3, 0, -1):
            self.__draw_and_infect(i)

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self._infection_deck.pop(1)
            self._infect_city(top_card, times=num_infections)
            self._infection_discard_pile.append(top_card)

    def _infect_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        outbreak = False
        city_state = self.get_city(city)
        if color is None:
            color = city_state.get_color()
        if self._cures[color] and self._cubes[color] == COUNT_CUBES:
            # virus has been eradicated
            return outbreak
        for _ in itertools.repeat(None, times):
            outbreak = self.get_city(city).inc_infection(color)
            if outbreak:
                break
            self._cubes[color] -= 1

        return outbreak

    def _treat_city(self, city: City, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        city_state = self.get_city(city)
        if color is None:
            color = city_state.get_color()

        for _ in itertools.repeat(None, 3 if self._cures[color] else times):
            is_empty = self.get_city(city).dec_infection(color)
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
        if self._infections == 0 and self._resilient:
            pass
        elif self._infections < self.infection_rate():
            top_card = self._infection_deck.pop(0)
            outbreak = self._infect_city(top_card)
            if outbreak:
                self._outbreak(top_card, self.get_city(top_card).get_color())
            self._infection_discard_pile.append(top_card)
            self._infections += 1
        if self._infections == self.infection_rate() or self._resilient:
            self._infections = 0
            if self._infections == 0:
                self._resilient = False
            self._active_player = self.get_next_player()
            self._phase = Phase.ACTIONS

        return self.get_possible_actions()

    def active_player(self) -> PlayerState:
        return self._players[self._active_player]

    def get_next_player(self) -> PlayerColor:
        list_of_player_colors = list(self._players.keys())
        index_of_active_player = list_of_player_colors.index(self._active_player)
        return list_of_player_colors[(index_of_active_player + 1) % len(list_of_player_colors)]

    def get_possible_actions(self, player: PlayerColor = None) -> Set[ActionInterface]:
        if player is None:
            player = self._active_player

        possible_actions: Set[ActionInterface] = self.get_possible_event_actions()

        # check all player hands
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
        return self.get_city(city).get_neighbors()

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

    def get_city(self, city: City) -> CityState:
        return self._cities[city]

    def infection_rate(self) -> int:
        return INFECTIONS_RATES[self._infection_rate_marker]

    def infect(self):
        for _ in itertools.repeat(None, self.infection_rate()):
            top_card = self._infection_deck.pop(0)
            outbreak = self._infect_city(top_card)
            if outbreak:
                self._outbreak(top_card, self.get_city(top_card).get_color())
            self._infection_discard_pile.append(top_card)

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
            return []

    def get_player_cards(self, player: PlayerColor = None):
        if player is None:
            player = self._active_player
        return self._players[player].get_cards()

    def player_cards_to_string(self, player: PlayerColor = None) -> str:
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

            neighbors = self.get_city(city).get_neighbors()
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(city)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self, player_count: int):
        for player in self._players.values():
            player.add_cards(self.draw_player_cards(count=TOTAL_STARTING_PLAYER_CARDS - player_count))

    def move_player(self, move: Movement, player=None):
        destination_city = move.destination
        if player is None:
            player = self._active_player

        if move.type == MovementAction.DRIVE:
            assert destination_city in self.get_city(self.get_player_current_city(player)).get_neighbors()
        if move.type == MovementAction.DIRECT_FLIGHT:
            self._players[player].remove_card(destination_city)
        if move.type == MovementAction.CHARTER_FLIGHT:
            self._players[player].remove_card(self.get_player_current_city(player))
        if move.type == MovementAction.SHUTTLE_FLIGHT:
            assert (
                self.get_city(self.get_player_current_city(player)).has_research_station()
                and self.get_city(destination_city).has_research_station()
            )

        self._players[player].set_city(destination_city)

    def get_players(self) -> Dict[PlayerColor, PlayerState]:
        return self._players

    def get_phase(self) -> Phase:
        return self._phase

    def get_player_current_city(self, player: PlayerColor) -> City:
        return self._players[player].get_city()

    def other_action(self, action: Other, player: PlayerColor = None):
        if player is None:
            player = self._active_player

        if action.type == OtherAction.TREAT_DISEASE:
            self._treat_city(action.city, action.target_virus)
        elif action.type == OtherAction.BUILD_RESEARCH_STATION:
            self._players[player].remove_card(action.city)
            self.get_city(action.city).build_research_station()
            self._research_stations -= 1
        elif action.type == OtherAction.DISCOVER_CURE:
            for card in action.cure_card_combination:
                self._players[player].remove_card(card)
            self._cures[action.target_virus] = True
        elif action.type == OtherAction.SHARE_KNOWLEDGE:
            self._players[action.player].remove_card(action.card)
            self._players[action.target_player].add_card(action.card)

    def get_possible_move_actions(self, player: PlayerColor = None) -> Set[Movement]:
        if player is None:
            player = self._players[self._active_player]
        else:
            player = self._players[player]

        current_city = player.get_city()
        # drives / ferries
        moves = set(map(lambda c: Movement(MovementAction.DRIVE, c), self.get_neighbors(current_city)))

        # direct flights
        direct_flights = set(
            map(
                lambda c: Movement(MovementAction.DIRECT_FLIGHT, c),
                player.get_city_cards(),
            )
        )
        try:
            direct_flights.remove(current_city)
        except KeyError:
            # dont care if player has not own city
            pass

        # charter flights
        charter_flights = set(
            map(
                lambda c: Movement(MovementAction.CHARTER_FLIGHT, c),
                CITIES.keys() if current_city in player.get_cards() else [],
            )
        )
        # shuttle flights between two cities with research station
        shuttle_flights: Set[Movement] = set()
        if self.get_city(current_city).has_research_station():
            shuttle_flights = set(
                Movement(MovementAction.SHUTTLE_FLIGHT, cid)
                for cid, loc in self.get_cities().items()
                if loc.has_research_station() and cid != current_city
            )
        return moves.union(direct_flights).union(charter_flights).union(shuttle_flights)

    def get_city_color(self, city: City) -> Virus:
        return self.get_city(city).get_color()

    def get_possible_other_actions(self, player: PlayerColor = None) -> Set[Other]:
        if player is None:
            player_color = self._active_player
        else:
            player_color = player

        player = self._players[player_color]

        current_city = player.get_city()
        possible_actions: Set[Other] = set()

        # What is treatable?
        for virus, count in self.get_city(current_city).get_viral_state().items():
            if count > 0:
                possible_actions.add(Other(OtherAction.TREAT_DISEASE, current_city, target_virus=virus))

        # Can I build research station?
        if current_city in player.get_cards() and self._research_stations > 0:
            possible_actions.add(Other(OtherAction.BUILD_RESEARCH_STATION, current_city))

        # Can I discover a cure at this situation?
        if self.get_city(current_city).has_research_station():
            player_card_viruses = [self.get_city_color(card) for card in player.get_cards() if isinstance(card, City)]
            for virus, count in Counter(player_card_viruses).items():
                if count >= 5 and not self._cures[virus]:
                    potential_cure_cards: List[City] = list(filter(lambda c: self.get_city_color(c) == virus, player.get_city_cards()))

                    for cure_cards in list(itertools.combinations(potential_cure_cards, 5)):
                        possible_actions.add(
                            Other(
                                OtherAction.DISCOVER_CURE,
                                current_city,
                                target_virus=virus,
                                cure_card_combination=frozenset(cure_cards),
                            )
                        )

        # Can I share knowledge?
        players_in_city = {c: p for c, p in self._players.items() if p.get_city() == current_city}
        if len(players_in_city) > 1:
            for pc, p in players_in_city.items():
                if current_city in p.get_cards():
                    if pc == player_color:
                        # give card to other player
                        share_with_others = set(
                            Other(
                                OtherAction.SHARE_KNOWLEDGE,
                                current_city,
                                card=current_city,
                                player=player_color,
                                target_player=other,
                            )
                            for other in players_in_city.keys()
                            if other != player_color
                        )
                        possible_actions = possible_actions.union(share_with_others)
                    else:
                        # get card from other player
                        possible_actions.add(
                            Other(
                                OtherAction.SHARE_KNOWLEDGE,
                                current_city,
                                card=current_city,
                                player=pc,
                                target_player=player_color,
                            )
                        )
        return possible_actions

    def event_action(self, event: Event):
        event_type = event.type
        if event_type == EventCard.FORECAST:
            self._infection_discard_pile[:6] = event.forecast
            self._players[event.player].remove_card(EventCard.FORECAST)
        elif event_type == EventCard.GOVERNMENT_GRANT:
            self.get_city(event.destination).build_research_station()
            self._players[event.player].remove_card(EventCard.GOVERNMENT_GRANT)
        elif event_type == EventCard.AIRLIFT:
            self._players[event.target_player].set_city(event.destination)
            self._players[event.player].remove_card(EventCard.AIRLIFT)
        elif event_type == EventCard.RESILIENT_POPULATION:
            self._infection_discard_pile.remove(event.discard_card)
            self._players[event.player].remove_card(EventCard.RESILIENT_POPULATION)
        elif event_type == EventCard.ONE_QUIET_NIGHT:
            self._resilient = True
            self._players[event.player].remove_card(EventCard.ONE_QUIET_NIGHT)

    def get_possible_event_actions(self) -> Set[Event]:
        # TODO: search every player

        player_color = self._active_player
        player = self._players[player_color]

        possible_actions: Set[Event] = set()
        if EventCard.RESILIENT_POPULATION in player.get_cards():
            for card in self._infection_discard_pile:
                possible_actions.add(Event(EventCard.RESILIENT_POPULATION, player=player_color, discard_card=card))

        if EventCard.AIRLIFT in player.get_cards():
            for city in self.get_cities().keys():
                for p, _ in filter(lambda pcp: pcp[1].get_city() != city, self.get_players().items()):
                    possible_actions.add(
                        Event(EventCard.AIRLIFT, player=player_color, target_player=p, destination=city)
                    )

        if EventCard.FORECAST in player.get_cards():
            for permutation in itertools.permutations(self._infection_deck[:6]):
                possible_actions.add(Event(EventCard.FORECAST, player=player_color, forecast=tuple(permutation)))

        if EventCard.GOVERNMENT_GRANT in player.get_cards() and self._research_stations > 0:
            for city, _ in filter(lambda cid: not cid[1].has_research_station(), self.get_cities().items()):
                possible_actions.add(Event(EventCard.GOVERNMENT_GRANT, player=player_color, destination=city))
        if EventCard.ONE_QUIET_NIGHT in player.get_cards():
            possible_actions.add(Event(EventCard.ONE_QUIET_NIGHT, player=player_color))

        return possible_actions

    def throw_card_action(self, action: ThrowCard):
        assert isinstance(action, ThrowCard)
        self._players[action.player].remove_card(action.card)
