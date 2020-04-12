import itertools
from typing import List

from pandemic.simulation.actions import others
from pandemic.simulation.actions.others import num_cards_for_cure
from pandemic.simulation.model.actions import (
    Event,
    Forecast,
    GovernmentGrant,
    Airlift,
    ResilientPopulation,
    OneQuietNight,
    MoveResearchStation,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.enums import Character
from pandemic.simulation.model.phases import ChooseCardsPhase, Phase
from pandemic.simulation.state import State


def event_action(state: State, event: Event):
    if isinstance(event, Forecast):
        state.previous_phase = state.phase
        state.phase = Phase.FORECAST
        state.play_card(event.player, EventCard.FORECAST)
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
        __init_forecast(state)
        return []
    elif state.phase == Phase.MOVE_STATION:
        return [
            MoveResearchStation(state.active_player, move_from=c)
            for c, s in state.cities.items()
            if s.has_research_station() and not c == state.last_build_research_station
        ]
    elif state.phase == Phase.CURE_VIRUS:
        __init_cure_virus(state)
        return []

    possible_actions: List[Event] = list()
    extend = possible_actions.extend
    for player, player_state in state.players.items():
        for card in player_state.event_cards:
            extend(__action_for_event_card(state, player, card))

    return possible_actions


def __action_for_event_card(state: State, character: Character, event_card: EventCard) -> List[Event]:

    if event_card == EventCard.RESILIENT_POPULATION:
        return __resilient_population(state, character)

    if event_card == EventCard.AIRLIFT:
        return __airlift(state, character)

    if event_card == EventCard.FORECAST:
        return [Forecast(player=character)] if len(state.infection_deck) > 0 else []

    if event_card == EventCard.GOVERNMENT_GRANT:
        return __government_grant(state, character)

    if event_card == EventCard.ONE_QUIET_NIGHT:
        return [OneQuietNight(player=character)]


def __forecast_after(s, _, c):
    s.infection_deck[:6] = c


def __init_forecast(state: State):
    active_player = state.active_player

    top_cards = set(state.infection_deck[:6])
    ccp = ChooseCardsPhase(
        next_phase=state.previous_phase,
        cards_to_choose_from=top_cards,
        count=len(top_cards),
        player=active_player,
        after=__forecast_after,
    )

    state.start_choose_cards_phase(ccp)


def __cure_virus_after(state, p, cards):
    state.cures[state.virus_to_cure] = True
    for card in cards:
        state.play_card(p, card)
    medic = state.players.get(Character.MEDIC, None)
    if medic:
        state.treat_city(medic.city, state.virus_to_cure, 3)
    state.virus_to_cure = None


def __init_cure_virus(state: State):
    active_player = state.active_player
    cure_cards = {
        city for city in state.players[active_player].city_cards if state.cities[city].color == state.virus_to_cure
    }
    ccp = ChooseCardsPhase(
        next_phase=state.previous_phase,
        cards_to_choose_from=cure_cards,
        count=num_cards_for_cure(state.active_player),
        player=active_player,
        after=__cure_virus_after,
    )

    state.start_choose_cards_phase(ccp)


def __resilient_population(state: State, character: Character) -> List[Event]:
    # TODO: split in two phases
    return [ResilientPopulation(player=character, discard_city=card) for card in state.infection_discard_pile]


def __airlift(state: State, character: Character) -> List[Event]:
    return [
        Airlift(player=character, target_player=p, destination=city)
        for city, (p, c) in itertools.product(state.cities.keys(), state.players.items())
        if c.city != city
    ]


def __government_grant(state: State, character: Character) -> List[Event]:
    return [
        GovernmentGrant(player=character, target_city=city)
        for city, s in state.cities.items()
        if not s.has_research_station()
    ]
