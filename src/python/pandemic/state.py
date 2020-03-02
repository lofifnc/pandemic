from typing import List, Dict, Set

from pandemic.model.actions import ActionInterface, Movement, Other
from pandemic.model.enums import PlayerColor, MovementAction, OtherAction
from random import shuffle
import itertools
import numpy as np
import logging

from pandemic.model.constants import *
from pandemic.model.player import Player


class State:
    def __init__(self):

        self._player_locations = {
            PlayerColor.BLUE: PLAYER_START,
            PlayerColor.GREEN: PLAYER_START,
            PlayerColor.RED: PLAYER_START,
            PlayerColor.WHITE: PLAYER_START,
        }

        self._cubes = {
            Virus.YELLOW: 24,
            Virus.BLACK: 24,
            Virus.BLUE: 24,
            Virus.RED: 24,
        }

        self._players = {
            PlayerColor.RED: Player(),
            PlayerColor.BLUE: Player(),
            PlayerColor.GREEN: Player(),
            PlayerColor.WHITE: Player(),
        }

        self._active_player = PlayerColor.RED
        self._player_actions = PLAYER_ACTIONS

        self._outbreaks = 0
        self._infection_rate_marker = 0

        self._infection_deck: List[str] = list(LOCATIONS.keys())
        shuffle(self._infection_deck)
        self._infection_discard_pile: List[str] = []

        self._player_deck: List[str] = list(LOCATIONS.keys())
        shuffle(self._player_deck)
        self._serve_player_cards()
        self._prepare_player_deck()
        self._player_discard_pile: List[str] = []

        self._locations = LOCATIONS.copy()
        self._add_neighbors_to_locations()

        self._init_infection_markers()

    def _init_infection_markers(self):
        for i in range(3, 0, -1):
            print(i)
            self.__draw_and_infect(i)

    def __draw_and_infect(self, num_infections: int):
        for _ in itertools.repeat(None, 3):
            top_card = self._infection_deck.pop(1)
            self._infect_city(top_card, times=num_infections)
            self._infection_discard_pile.append(top_card)

    def _infect_city(self, city: str, color: Virus = None, times: int = 1) -> bool:
        outbreak = False
        location = self.get_location(city)
        if color is None:
            color = location.get_color()
        for _ in itertools.repeat(None, times):
            outbreak = self.get_location(city).inc_infection(color)
            if outbreak:
                break
            self._cubes[color] -= 1

        return outbreak

    def _treat_city(self, city: str, color: Virus = None, times: int = 1) -> bool:
        is_empty = False
        location = self.get_location(city)
        if color is None:
            color = location.get_color()
        for _ in itertools.repeat(None, times):
            is_empty = self.get_location(city).dec_infection(color)
            if is_empty:
                break
            self._cubes[color] += 1

        return is_empty

    def turn(self, action: ActionInterface) -> Set[ActionInterface]:
        if self._player_actions > 1:
            if isinstance(action, Movement):
                # TODO: check if move possible
                self.move_player(action.destination)
            elif isinstance(action, Other):
                self.other_action(action)
            self._player_actions -= 1

        else:
            self.draw_player_cards()
            self.infect()

        return self.get_possible_moves()

    def get_possible_moves(self, player=None) -> Set[Movement]:
        if player is None:
            player = self._players[self._active_player]
        else:
            player = self._players[player]

        city = player.get_city()
        moves = set(
            map(lambda c: Movement(MovementAction.DRIVE, c), self.get_neighbors(city))
        )
        direct_flights = set(player.get_cards())
        direct_flights.remove(city)
        charter_flights = LOCATIONS.keys() if city in player.get_cards() else []
        return moves  # TODO: only direct moves for the moment

    def get_neighbors(self, city: str) -> Set[str]:
        return self.get_location(city).get_neighbors()

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
            self._locations[start].add_neighbor(end)
            self._locations[end].add_neighbor(start)

    def get_locations(self) -> Dict[str, Location]:
        return self._locations

    def get_location(self, name: str) -> Location:
        return self._locations[name]

    def infection_rate(self) -> int:
        print(self._infection_rate_marker)
        return INFECTIONS_RATES[self._infection_rate_marker]

    def infect(self):
        for _ in itertools.repeat(None, self.infection_rate()):
            top_card = self._infection_deck.pop(0)
            outbreak = self._infect_city(top_card)
            if outbreak:
                self._outbreak(top_card, self.get_location(top_card).get_color())
            self._infection_discard_pile.append(top_card)

    def report(self) -> str:
        min_cubes = min(self._cubes, key=self._cubes.get)
        return (
            "player_cards_left={player_deck_size},"
            "infection_rate={infection_rate},"
            "outbreaks={outbreaks},"
            "min_cubes={min_cubes}"
        ).format(
            player_deck_size=len(self._player_deck),
            infection_rate=self.infection_rate(),
            outbreaks=self._outbreaks,
            min_cubes="%s:%s" % (min_cubes, self._cubes[min_cubes]),
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

    """
    Function to simulate outbreaks
    """

    def _outbreak(self, location: str, color: Virus, outbreaks: Set[str] = None):
        if outbreaks is None:
            outbreaks = set()
        if location not in outbreaks:
            self._outbreaks += 1
            neighbors = self.get_location(location).get_neighbors()
            for n in neighbors:
                has_outbreak = self._infect_city(n, color, 1)
                if has_outbreak:
                    outbreaks.add(location)
                    self._outbreak(n, color, outbreaks)

    def _serve_player_cards(self):
        for player in self._players.values():
            player.add_cards(self.draw_player_cards(count=2))

    def move_player(self, destination: str, player=None):
        if player is None:
            player = self._active_player
        self._players[player].set_city(destination)

    def get_players(self) -> Dict[PlayerColor, Player]:
        return self._players

    def other_action(self, action: Other, player: PlayerColor = None):
        if player is None:
            player = self._active_player

        if action.type == OtherAction.TREAT_DISEASE:
            self._treat_city(action.city, action.target_virus)
        elif action.type == OtherAction.BUILD_RESEARCH_STATION:
            # TODO: add research station and remove card
            pass
        elif action.type == OtherAction.DISCOVER_CURE:
            # TODO: create cure and discover cards
            pass
        elif action.type == OtherAction.SHARE_KNOWLEDGE:
            # TODO: move cards around
            pass

    def get_possible_actions(self, player: PlayerColor = None):
        if player is None:
            player = self._players[self._active_player]
        else:
            player = self._players[player]

        current_city = player.get_city()
        possible_actions: Set[Other] = set()

        # What is treatable?
        for virus, count in self.get_location(current_city).get_viral_state().items():
            if count > 0:
                possible_actions.add(
                    Other(OtherAction.TREAT_DISEASE, current_city, target_virus=virus)
                )

        # Can I build research station?
        # TODO: add research station and remove card
        pass

        # Can I discover a cure at this situation?
        # TODO: create cure and discover cards
        pass

        # Can I discover a cure at this situation?
        # TODO: move cards around
        pass
