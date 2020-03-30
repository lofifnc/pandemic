import itertools
from typing import List

from pandemic.simulation.actions import others
from pandemic.simulation.model.actions import (
    Event,
    Forecast,
    ForecastOrder,
    GovernmentGrant,
    Airlift,
    ResilientPopulation,
    OneQuietNight,
    MoveResearchStation,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.enums import Character
from pandemic.simulation.state import State, Phase


def event_action(state: State, event: Event):
    if isinstance(event, Forecast):
        state.previous_phase = state.phase
        state.phase = Phase.FORECAST
        state.play_card(event.player, EventCard.FORECAST)
    elif isinstance(event, ForecastOrder):
        state.infection_deck[:6] = event.forecast
        state.phase = state.previous_phase
    elif isinstance(event, GovernmentGrant):
        others.build_research_station(state, event.target_city)
        state.play_card(event.player, EventCard.GOVERNMENT_GRANT)
    elif isinstance(event, Airlift):
        state.move_player_to_city(event.target_player, event.destination)
        state.play_card(event.player, EventCard.AIRLIFT)
    elif isinstance(event, ResilientPopulation):
        state.infection_discard_pile.remove(event.discard_city)
        state.play_card(event.player, EventCard.RESILIENT_POPULATION)
    elif isinstance(event, OneQuietNight):
        state.one_quiet_night = True
        state.play_card(event.player, EventCard.ONE_QUIET_NIGHT)
    elif isinstance(event, MoveResearchStation):
        state.cities[event.move_from].remove_research_station()
        state.phase = state.previous_phase


def get_possible_event_actions(state: State) -> List[Event]:

    if state.phase == Phase.FORECAST:
        return __get_forecast_order(state)
    if state.phase == Phase.MOVE_STATION:
        return [
            MoveResearchStation(state.active_player, move_from=c)
            for c, s in state.cities.items()
            if s.has_research_station() and not c == state.last_build_research_station
        ]

    possible_actions: List[Event] = list()
    extend = possible_actions.extend
    for player, player_state in state.players.items():
        for card in player_state.event_cards:
            extend(__action_for_event_card(state, player, card))

    return possible_actions


def __action_for_event_card(state: State, character: Character, event_card: EventCard) -> List[Event]:

    possible_actions: List[Event] = list()
    if event_card == EventCard.RESILIENT_POPULATION:
        __add_resilient_population(state, character, possible_actions)

    if event_card == EventCard.AIRLIFT:
        __add_airlift(state, character, possible_actions)

    if event_card == EventCard.FORECAST:
        possible_actions.append(Forecast(player=character))

    if event_card == EventCard.GOVERNMENT_GRANT:
        __add_government_grant(state, character, possible_actions)

    if event_card == EventCard.ONE_QUIET_NIGHT:
        possible_actions.append(OneQuietNight(player=character))

    return possible_actions


def __get_forecast_order(state: State) -> List[Event]:
    active_player = state.active_player
    return [
        ForecastOrder(active_player, forecast=tuple(permutation))
        for permutation in itertools.permutations(state.infection_deck[:6])
    ]


def __add_resilient_population(state: State, character: Character, possible_actions: List[Event]):
    possible_actions.extend(
        ResilientPopulation(player=character, discard_city=card) for card in state.infection_discard_pile
    )


def __add_airlift(state: State, character: Character, possible_actions: List[Event]):
    possible_actions.extend(
        Airlift(player=character, target_player=p, destination=city)
        for city, (p, c) in itertools.product(state.get_cities().keys(), state.players.items())
        if c.city != city
    )


def __add_government_grant(state: State, character: Character, possible_actions: List[Event]):
    possible_actions.extend(
        GovernmentGrant(player=character, target_city=city)
        for city, s in state.cities.items()
        if not s.has_research_station()
    )
