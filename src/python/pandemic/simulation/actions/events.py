import itertools
from typing import List

from pandemic.simulation.model.actions import (
    Event,
    Forecast,
    ForecastOrder,
    GovernmentGrant,
    Airlift,
    ResilientPopulation,
    OneQuietNight,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.enums import Character
from pandemic.simulation.state import State, Phase


def event_action(state: State, event: Event):
    if isinstance(event, Forecast):
        state.previous_phase = state.phase
        print("start forecast")
        state.phase = Phase.FORECAST
        state.play_card(event.player, EventCard.FORECAST)
    elif isinstance(event, ForecastOrder):
        state.infection_deck[:6] = event.forecast
        print("execute")
        state.phase = state.previous_phase
    elif isinstance(event, GovernmentGrant):
        state.get_city_state(event.target_city).build_research_station()
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


def get_possible_event_actions(state: State) -> List[Event]:

    if state.phase == Phase.FORECAST:
        return __get_forecast_order(state)

    possible_actions: List[Event] = list()
    players_with_event_cards = [(p, s, s.get_event_cards()) for p, s in state.players.items()]
    for player, player_state, event_cards in players_with_event_cards:
        possible_actions.extend(
            itertools.chain.from_iterable(__action_for_event_card(state, player, card) for card in event_cards)
        )

    return possible_actions


def __action_for_event_card(state: State, player_color: Character, event_card: EventCard) -> List[Event]:

    possible_actions: List[Event] = list()
    if event_card == EventCard.RESILIENT_POPULATION:
        for card in state.infection_discard_pile:
            possible_actions.append(ResilientPopulation(player=player_color, discard_city=card))

    if event_card == EventCard.AIRLIFT:
        for city in state.get_cities().keys():
            for p, _ in filter(lambda pcp: pcp[1].get_city() != city, state.players.items()):
                possible_actions.append(Airlift(player=player_color, target_player=p, destination=city))

    if event_card == EventCard.FORECAST:
        possible_actions.append(Forecast(player=player_color))

    # TODO: fix grant
    if event_card == EventCard.GOVERNMENT_GRANT:
        for city, _ in filter(lambda cid: not cid[1].has_research_station(), state.cities.items()):
            possible_actions.append(GovernmentGrant(player=player_color, target_city=city))

    if event_card == EventCard.ONE_QUIET_NIGHT:
        possible_actions.append(OneQuietNight(player=player_color))

    return possible_actions


def __get_forecast_order(state: State) -> List[Event]:
    return [
        ForecastOrder(state.active_player, forecast=tuple(permutation))
        for permutation in itertools.permutations(state.infection_deck[:6])
    ]
