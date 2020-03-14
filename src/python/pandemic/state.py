from typing import List, Dict, Set

from pandemic.model.actions import ActionInterface, Movement, Other
from pandemic.model.enums import PlayerColor, MovementAction, OtherAction
from random import shuffle
import itertools
import numpy as np
import logging

from pandemic.model.constants import *
from pandemic.model.player import Player
from collections import Counter

class State:
    def __init__(self):

        # players
        self._players: Dict[PlayerColor, Player] = {
            PlayerColor(n): Player() for n in range(1, PLAYER_COUNT + 1)
        }

        self._active_player: PlayerColor = list(self._players.keys())[0]

        # counters
        self._research_stations = 5
        self._outbreaks = 0
        self._infection_rate_marker = 0
        self._cubes = {Virus.YELLOW: 24, Virus.BLACK: 24, Virus.BLUE: 24, Virus.RED: 24}
        self._player_actions = PLAYER_ACTIONS

        # cards
        self._infection_deck: List[str] = list(CITIES.keys())
        shuffle(self._infection_deck)
        self._infection_discard_pile: List[str] = []

        self._player_deck: List[str] = list(CITIES.keys())
        shuffle(self._player_deck)
        self._serve_player_cards()
        self._prepare_player_deck()
        self._player_discard_pile: List[str] = []

        self._cities = CITIES.copy()
        self._add_neighbors_to_locations()

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

    def _infect_city(self, city_id: str, color: Virus = None, times: int = 1) -> bool:
        outbreak = False
        location = self.get_city(city_id)
        if color is None:
            color = location.get_color()
        for _ in itertools.repeat(None, times):
            outbreak = self.get_city(city_id).inc_infection(color)
            if outbreak:
                break
            self._cubes[color] -= 1

        return outbreak

    def _treat_city(self, city_id: str, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        location = self.get_city(city_id)
        if color is None:
            color = location.get_color()
        for _ in itertools.repeat(None, times):
            is_empty = self.get_city(city_id).dec_infection(color)
            if is_empty:
                break
            self._cubes[color] += 1

        return is_empty

    def turn(self, action: ActionInterface) -> Set[ActionInterface]:
        if self._player_actions > 0:
            if isinstance(action, Movement):
                self.move_player(action)
            elif isinstance(action, Other):
                self.other_action(action)
            self._player_actions -= 1
        if self._player_actions == 0:
            self.draw_player_cards()
            self.infect()
            self._active_player = PlayerColor(
                self._active_player.value + 1 % len(self._players)
            )
            self._player_actions = PLAYER_ACTIONS

        return self.get_possible_actions()

    def get_possible_actions(self, player: PlayerColor = None) -> Set[ActionInterface]:
        return self.get_possible_move_actions(player).union(
            self.get_possible_other_actions(player)
        )

    def get_neighbors(self, city_id: str) -> Set[str]:
        return self.get_city(city_id).get_neighbors()

    def _prepare_player_deck(self):
        prepared_deck: List[str] = []
        city_cards = self._player_deck
        shuffle(city_cards)
        chunks = np.array_split(city_cards, 5)
        for c in chunks:
            d = list(c)
            d.append(EPIDEMIC_CARD)
            shuffle(d)
            prepared_deck.extend(d)
        self._player_deck = prepared_deck

    def _add_neighbors_to_locations(self):
        for con in CONNECTIONS:
            start, end = con[0], con[1]
            self._cities[start].add_neighbor(end)
            self._cities[end].add_neighbor(start)

    def get_cities(self) -> Dict[str, City]:
        return self._cities

    def get_city(self, city_id: str) -> City:
        return self._cities[city_id]

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
            active_player="%s:%s"
            % (self._active_player.name.lower(), self._player_actions),
            player_deck_size=len(self._player_deck),
            infection_rate=self.infection_rate(),
            outbreaks=self._outbreaks,
            min_cubes="%s:%s" % (min_cubes.name, self._cubes[min_cubes]),
        )

    def _epidemic(self):
        self._infection_rate_marker += 1
        bottom_card = self._infection_deck.pop(-1)
        logging.info("Epidemic in %s!" % bottom_card)
        self._infect_city(bottom_card, times=3)
        discard_pile = self._infection_discard_pile.copy() + [bottom_card]
        shuffle(discard_pile)
        self._infection_deck = discard_pile + self._infection_deck

    def draw_player_cards(self, count: int = 2) -> List[str]:
        drawn_cards: List[str] = []
        for _ in itertools.repeat(None, count):
            try:
                top_card = self._player_deck.pop(0)
                if top_card == EPIDEMIC_CARD:
                    self._epidemic()
                else:
                    drawn_cards.append(top_card)
            except IndexError:
                logging.info("you lost no more cards")
                return []
        return drawn_cards

    def get_player_cards(self, player: PlayerColor = None):
        if player is None:
            player = self._active_player
        return self._players[player].get_cards()

    def get_actions_left(self):
        return self._player_actions

    """
    Function to simulate outbreaks
    """

    def _outbreak(self, city_id: str, color: Virus, outbreaks: Set[str] = None):
        if outbreaks is None:
            outbreaks = set()
        if city_id not in outbreaks:
            self._outbreaks += 1
            neighbors = self.get_city(city_id).get_neighbors()
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(city_id)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self):
        for player in self._players.values():
            player.add_cards(
                self.draw_player_cards(count=TOTAL_STARTING_PLAYER_CARDS - PLAYER_COUNT)
            )

    def move_player(self, move: Movement, player=None):
        destination_city_id = move.destination
        if player is None:
            player = self._active_player

        if move.type == MovementAction.DRIVE:
            assert (
                destination_city_id
                in self.get_city(self.get_player_location(player)).get_neighbors()
            )
        if move.type == MovementAction.DIRECT_FLIGHT:
            self._players[player].remove_card(destination_city_id)
        if move.type == MovementAction.CHARTER_FLIGHT:
            self._players[player].remove_card(self.get_player_location(player))
        if move.type == MovementAction.SHUTTLE_FLIGHT:
            assert (
                self.get_city(self.get_player_location(player)).has_research_station()
                and self.get_city(destination_city_id).has_research_station()
            )

        self._players[player].set_city(destination_city_id)

    def get_players(self) -> Dict[PlayerColor, Player]:
        return self._players

    def get_player_location(self, player: PlayerColor) -> str:
        return self._players[player].get_city_id()

    def other_action(self, action: Other, player: PlayerColor = None):
        if player is None:
            player = self._active_player

        if action.type == OtherAction.TREAT_DISEASE:
            self._treat_city(action.city_id, action.target_virus)
        elif action.type == OtherAction.BUILD_RESEARCH_STATION:
            self._players[player].remove_card(action.city_id)
            self.get_city(action.city_id).build_research_station()
            self._research_stations -= 1
            pass
        elif action.type == OtherAction.DISCOVER_CURE:
            # TODO: create cure and discover cards
            pass
        elif action.type == OtherAction.SHARE_KNOWLEDGE:
            # TODO: move cards around
            pass

    def get_possible_move_actions(self, player: PlayerColor = None) -> Set[Movement]:
        if player is None:
            player = self._players[self._active_player]
        else:
            player = self._players[player]

        current_city_id = player.get_city_id()
        # drives / ferries
        moves = set(
            map(
                lambda c: Movement(MovementAction.DRIVE, c),
                self.get_neighbors(current_city_id),
            )
        )

        # direct flights
        direct_flights = set(
            map(
                lambda c: Movement(MovementAction.DIRECT_FLIGHT, c),
                set(player.get_cards()),
            )
        )
        try:
            direct_flights.remove(current_city_id)
        except KeyError:
            # dont care if player has not own city
            pass

        # charter flights
        charter_flights = set(
            map(
                lambda c: Movement(MovementAction.DIRECT_FLIGHT, c),
                CITIES.keys() if current_city_id in player.get_cards() else [],
            )
        )
        # shuttle flights between two cities with research station
        shuttle_flights: Set[Movement] = set()
        if self.get_city(current_city_id).has_research_station():
            shuttle_flights = set(
                Movement(MovementAction.SHUTTLE_FLIGHT, cid)
                for cid, loc in self.get_cities().items()
                if loc.has_research_station()
            )
        return moves.union(direct_flights).union(charter_flights).union(shuttle_flights)

    def get_city_color(self, city_id) -> Virus:
        return self.get_city(city_id).get_color()

    def get_possible_other_actions(self, player: PlayerColor = None) -> Set[Other]:
        if player is None:
            player = self._players[self._active_player]
        else:
            player = self._players[player]

        current_city_id = player.get_city_id()
        possible_actions: Set[Other] = set()

        # What is treatable?
        for virus, count in self.get_city(current_city_id).get_viral_state().items():
            if count > 0:
                possible_actions.add(
                    Other(
                        OtherAction.TREAT_DISEASE, current_city_id, target_virus=virus
                    )
                )

        # Can I build research station?
        if current_city_id in player.get_cards() and self._research_stations > 0:
            possible_actions.add(
                Other(OtherAction.BUILD_RESEARCH_STATION, current_city_id)
            )

        # Can I discover a cure at this situation?
        if self.get_city(current_city_id).has_research_station():
            player_card_viruses = [(self.get_city_color(card), card) for card in player.get_cards()]
            for virus_card, count in Counter(player_card_viruses).items():
                print(virus_card, count)
                if count >= 5:
                    virus, card = virus_card
                    possible_actions.add(Other(OtherAction.DISCOVER_CURE, current_city_id, target_virus=virus))

        # Can I discover a cure at this situation?
        # TODO: move cards around
        return possible_actions
