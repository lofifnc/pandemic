import math
import random

from pandemic.model.actions import OneQuietNight, ResilientPopulation, Airlift, Forecast, GovernmentGrant
from pandemic.model.city_id import EventCard, City
from pandemic.model.enums import Character
from pandemic.state import State
from pandemic.test.utils import less_random_state


def test_quiet_event():
    state = State()
    active_player = state._active_player

    state._players[active_player].add_card(EventCard.ONE_QUIET_NIGHT)

    event = OneQuietNight(player=active_player)
    actions = state.get_possible_actions()
    assert event in actions
    state.step(event)
    assert state._resilient
    assert EventCard.ONE_QUIET_NIGHT not in state.get_player_cards()


def test_resilient_population(less_random_state):
    state = less_random_state()
    active_player = state._active_player

    state._players[active_player].add_card(EventCard.RESILIENT_POPULATION)
    discard_pile_top_card = state._infection_discard_pile[0]

    event = ResilientPopulation(player=active_player, discard_city=discard_pile_top_card)
    actions = state.get_possible_actions()
    assert len(set(state._infection_discard_pile)) == len(state._infection_discard_pile)
    assert len(list(filter(lambda a: isinstance(a, ResilientPopulation), actions))) == len(
        state._infection_discard_pile
    )
    assert event in actions
    state.step(event)
    assert discard_pile_top_card not in state._infection_discard_pile


def test_airlift(less_random_state):
    state = less_random_state()
    active_player = state._active_player

    state._players[active_player].add_card(EventCard.AIRLIFT)

    event = Airlift(player=active_player, target_player=Character.RESEARCHER, destination=City.MANILA)
    actions = state.get_possible_actions()
    assert event in actions
    state.step(event)
    assert state.get_player_current_city(Character.RESEARCHER) == City.MANILA
    assert EventCard.AIRLIFT not in state.get_player_cards(active_player)
    assert EventCard.AIRLIFT in state._player_discard_pile


def test_forecast(less_random_state):
    state = less_random_state()
    active_player = state._active_player

    state._players[active_player].add_card(EventCard.FORECAST)

    our_shuffle = state._infection_deck[:6].copy()
    random.shuffle(our_shuffle)
    event = Forecast(player=active_player, forecast=tuple(our_shuffle))
    actions = state.get_possible_actions()
    assert event in actions
    assert len(list(filter(lambda a: isinstance(a, Forecast), actions))) == math.factorial(6)
    state.step(event)
    assert our_shuffle == state._infection_deck[:6]


def test_government_grant(less_random_state):
    state = less_random_state()
    active_player = state._active_player

    state._players[active_player].add_card(EventCard.GOVERNMENT_GRANT)

    assert not state.get_city(City.BAGHDAD).has_research_station()
    event = GovernmentGrant(player=active_player, target_city=City.BAGHDAD)
    actions = state.get_possible_actions()
    assert event in actions
    assert GovernmentGrant(player=active_player, target_city=City.ATLANTA) not in actions
    state.step(event)
    assert state.get_city(City.BAGHDAD).has_research_station()
