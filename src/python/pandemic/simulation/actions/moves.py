import itertools
from typing import List, Set

from pandemic.simulation.model.actions import (
    Movement,
    DriveFerry,
    DirectFlight,
    CharterFlight,
    ShuttleFlight,
    OperationsFlight,
    Dispatch,
)
from pandemic.simulation.model.enums import Character
from pandemic.simulation.state import State, City, CITY_DATA


def move_player(state: State, move: Movement):
    destination_city = move.destination
    character = move.player

    if isinstance(move, DriveFerry):
        assert destination_city in CITY_DATA[state.get_player_current_city(character)].neighbors
    if isinstance(move, DirectFlight):
        state.play_card(state.active_player, destination_city)
    if isinstance(move, CharterFlight):
        state.play_card(state.active_player, state.get_player_current_city(character))
    if isinstance(move, ShuttleFlight):
        assert (
            state.cities[state.get_player_current_city(character)].has_research_station()
            and state.cities[destination_city].has_research_station()
        )
    if isinstance(move, OperationsFlight):
        state.play_card(character, move.discard_card)
        state.players[character].used_operations_expert_shuttle_move()

    state.move_player_to_city(character, destination_city)


# @profile
def get_possible_move_actions(state: State, character: Character = None) -> List[Movement]:
    if character is None:
        character = state.active_player

    player_state = state.players[character]

    moves: List[Movement] = __possible_moves(state, character, player_state.city_cards)

    # Dispatcher
    extend = moves.extend
    if character == Character.DISPATCHER:
        for c in state.players.keys():
            extend(__possible_moves(state, c, player_state.city_cards))
        for f, t in itertools.permutations(state.players.keys(), 2):
            __add_dispatches(moves, f, state, t)
    return moves


def __add_dispatches(moves: List[Movement], from_char: Character, state: State, to_char: Character):
    moves.append(Dispatch(from_char, state.get_player_current_city(to_char)))


# @profile
def __possible_moves(state: State, character: Character, city_cards: Set[City]) -> List[Movement]:
    player_state = state.players[character]
    current_city = player_state.city
    # drives / ferries
    neighbor_cities = CITY_DATA[current_city].neighbors
    moves = [DriveFerry(character, c) for c in neighbor_cities]

    # direct flights
    direct_flights = [DirectFlight(character, c) for c in city_cards if c != current_city]

    # charter flights
    charter_flights: List[Movement] = [
        CharterFlight(character, c)
        for c in (state.cities.keys() if current_city in city_cards else [])
        if c != current_city
    ]
    # shuttle flights between two cities with research station
    shuttle_flights: List[Movement] = list()
    if state.cities[current_city].has_research_station():
        city_states = state.cities.items()
        shuttle_flights = [
            ShuttleFlight(character, cid)
            for cid, loc in city_states
            if loc.has_research_station() and cid != current_city
        ]

    # operations expert charter flights
    operation_flights: List[Movement] = list()
    if (
        state.active_player == Character.OPERATIONS_EXPERT
        and state.cities[current_city].has_research_station()
        and player_state.operations_expert_has_charter_flight()
    ):
        cities = state.cities.keys()
        operation_flights = [
            OperationsFlight(character, destination=city, discard_card=card)
            for city, card in itertools.product(cities, player_state.city_cards)
        ]

    return moves + direct_flights + charter_flights + shuttle_flights + operation_flights
