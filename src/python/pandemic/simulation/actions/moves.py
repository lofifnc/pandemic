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
from pandemic.simulation.state import State, City


def move_player(state: State, move: Movement):
    destination_city = move.destination
    character = move.player

    if isinstance(move, DriveFerry):
        assert destination_city in state.get_city_state(state.get_player_current_city(character)).get_neighbors()
    if isinstance(move, DirectFlight):
        state.play_card(state.active_player, destination_city)
    if isinstance(move, CharterFlight):
        state.play_card(state.active_player, state.get_player_current_city(character))
    if isinstance(move, ShuttleFlight):
        assert (
            state.get_city_state(state.get_player_current_city(character)).has_research_station()
            and state.get_city_state(destination_city).has_research_station()
        )
    if isinstance(move, OperationsFlight):
        state.play_card(character, move.discard_card)
        state.players[character].used_operations_expert_shuttle_move()

    state.move_player_to_city(character, destination_city)


def get_possible_move_actions(state: State, character: Character = None) -> List[Movement]:
    if character is None:
        character = state.active_player

    player_state = state.players[character]

    moves = __possible_moves(state, character, player_state.get_city_cards())

    # Dispatcher
    if character == Character.DISPATCHER:
        for c in state.players.keys():
            moves.extend(__possible_moves(state, c, player_state.get_city_cards()))
        for f, t in itertools.permutations(state.players.keys(), 2):
            moves.append(Dispatch(f, state.get_player_current_city(t)))

        state.players.keys()

    return moves


def __possible_moves(state: State, character: Character, city_cards: Set[City]) -> List[Movement]:
    player_state = state.players[character]
    current_city = player_state.get_city()
    # drives / ferries
    moves: List[Movement] = list(map(lambda c: DriveFerry(character, c), state.cities[current_city].get_neighbors()))

    # direct flights
    direct_flights = list(DirectFlight(character, c) for c in city_cards if c != current_city)

    # charter flights
    charter_flights: List[Movement] = [
        CharterFlight(character, c)
        for c in (state.cities.keys() if current_city in city_cards else [])
        if c != current_city
    ]
    # shuttle flights between two cities with research station
    shuttle_flights: List[Movement] = list()
    if state.get_city_state(current_city).has_research_station():
        shuttle_flights = list(
            ShuttleFlight(character, cid)
            for cid, loc in state.get_cities().items()
            if loc.has_research_station() and cid != current_city
        )

    # operations expert charter flights
    operation_flights: List[Movement] = list()
    if (
        state.active_player == Character.OPERATIONS_EXPERT
        and state.get_city_state(current_city).has_research_station()
        and player_state.operations_expert_has_charter_flight()
    ):
        for card in player_state.get_city_cards():
            operation_flights.extend(
                {
                    OperationsFlight(character, destination=c, discard_card=card)
                    for c in state.cities.keys()
                    if c != current_city
                }
            )

    return moves + direct_flights + charter_flights + shuttle_flights + operation_flights
