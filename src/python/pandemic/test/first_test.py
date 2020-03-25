from typing import Set, Type

import pytest

from pandemic.model.actions import (
    Event,
    ActionInterface,
    ThrowCard,
    DiscoverCure,
    ShareKnowledge,
    TreatDisease,
    ReserveCard,
    OneQuietNight)
from pandemic.model.city_id import EventCard
from pandemic.model.enums import Character, Virus, GameState
from pandemic.model.playerstate import PlayerState
from pandemic.state import State, Phase, City


@pytest.fixture
def less_random_state():
    def create_state(start_player: Character = Character.SCIENTIST):
        state = State()
        player_state = PlayerState()
        player_state._cards = {}
        state._players = {
            start_player: PlayerState(),
            Character.RESEARCHER if start_player.SCIENTIST else start_player.SCIENTIST: PlayerState(),
        }

        state._active_player = start_player
        return state

    return create_state


def test_cure_virus(less_random_state):
    state = less_random_state(start_player=Character.RESEARCHER)

    state.get_players()[Character.RESEARCHER]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
    }

    cure_action = DiscoverCure(
        target_virus=Virus.RED,
        card_combination=frozenset({City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}),
    )
    assert cure_action in state.get_possible_actions()

    state.step(cure_action)
    assert state._cures[Virus.RED]
    assert not state._cures[Virus.BLUE]
    assert not state._cures[Virus.BLACK]
    assert not state._cures[Virus.YELLOW]
    assert len(state.get_player_cards(Character.RESEARCHER)) == 0


def test_already_cured_combination(less_random_state):
    state = less_random_state(start_player=Character.RESEARCHER)

    state._active_player = Character.RESEARCHER
    state.get_players()[Character.RESEARCHER]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
    }
    state._cures[Virus.RED] = True

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset(
                {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
            ),
        )
        not in state.get_possible_actions()
    )


def test_multiple_cure_combinations(less_random_state):
    state = less_random_state(start_player=Character.RESEARCHER)

    state._active_player = Character.RESEARCHER
    state.get_players()[Character.RESEARCHER]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
    }

    actions = state.get_possible_actions()

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset((City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.SYDNEY)),
        )
        in actions
    )

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset(
                (City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.HONG_KONG, City.SYDNEY)
            ),
        )
        in actions
    )

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset((City.BANGKOK, City.HO_CHI_MINH_CITY, City.MANILA, City.HONG_KONG, City.SYDNEY)),
        )
        in actions
    )

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset((City.BANGKOK, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY)),
        )
        in actions
    )

    assert (
        DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset((City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY)),
        )
        in actions
    )


def test_player_change(less_random_state):
    state = less_random_state()
    active_player = state._active_player
    assert state.get_next_player() != active_player
    state._active_player = state.get_next_player()
    assert state.get_next_player() == active_player


def test_get_card_sharing(less_random_state):
    state = less_random_state()
    active_player = state._active_player
    other_player = state.get_next_player()
    try:
        state._players[other_player].remove_card(City.ATLANTA)
    except KeyError:
        pass
    state._players[other_player].add_card(City.ATLANTA)

    sharing_action = ShareKnowledge(card=City.ATLANTA, player=other_player, target_player=active_player)

    assert sharing_action in state.get_possible_other_actions()

    state.step(sharing_action)
    assert City.ATLANTA not in state.get_player_cards(other_player)
    assert City.ATLANTA in state.get_player_cards(active_player)

    assert sharing_action not in state.get_possible_other_actions()


def test_give_card_sharing(less_random_state):
    state = less_random_state()
    active_player = state._active_player
    other_player = state.get_next_player()

    state.get_players()[active_player].add_card(City.ATLANTA)

    sharing_action = ShareKnowledge(card=City.ATLANTA, player=active_player, target_player=other_player)

    assert sharing_action in state.get_possible_other_actions()

    state.step(sharing_action)

    assert City.ATLANTA not in state.get_player_cards(active_player)
    assert City.ATLANTA in state.get_player_cards(other_player)

    assert sharing_action not in state.get_possible_other_actions()


def filter_out_events(actions: Set[ActionInterface], clazz: Type) -> Set[ActionInterface]:
    return set(filter(lambda a: not isinstance(a, clazz), actions))


def test_whole_round():
    state = State()

    for i in range(1, 4):
        action = state.get_possible_actions()
        assert action != set()
        state.step(filter_out_events(action, Event).pop())
        assert state.get_phase() == Phase.ACTIONS

    action = state.get_possible_actions()
    assert action != set()
    state.step(filter_out_events(action, Event).pop())
    # draw phase
    assert state.get_phase() == Phase.DRAW_CARDS

    assert all(isinstance(action, Event) for action in state.get_possible_actions())
    state.step(None)

    if state.get_phase() == Phase.EPIDEMIC:
        state.step(None)

    assert state.get_phase() == Phase.DRAW_CARDS
    assert all(isinstance(action, Event) for action in state.get_possible_actions())
    state.step(None)

    # infection phase
    assert state.get_phase() == Phase.INFECTIONS

    assert all(isinstance(action, Event) for action in state.get_possible_actions())
    state.step(None)
    assert state.get_phase() == Phase.INFECTIONS
    assert all(isinstance(action, Event) for action in state.get_possible_actions())
    state.step(None)

    # next player
    assert state.get_phase() == Phase.ACTIONS


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


def test_treat_city():
    state = State()

    state.get_city(City.ATLANTA).inc_infection()
    virus_count = state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE]
    other = TreatDisease(City.ATLANTA, target_virus=Virus.BLUE)
    cube_count = state._cubes[Virus.BLUE]
    assert other in state.get_possible_actions()
    state.step(other)
    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == virus_count - 1
    assert state._cubes[Virus.BLUE] == cube_count + 1


def test_treat_city_with_cure():
    state = State()

    # in
    state._infect_city(City.ATLANTA, times=3)
    state._cures[Virus.BLUE] = True

    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == 3
    other = TreatDisease(City.ATLANTA, target_virus=Virus.BLUE)
    assert other in state.get_possible_actions()
    state.step(other)
    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == 0


def test_infect_city_with_eradicated_virus():
    state = State()

    # cheat and pretend virus is eradicated
    state._cures[Virus.BLUE] = True
    state._cubes[Virus.BLUE] = 24
    state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] = 0

    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == 0
    state._infect_city(City.ATLANTA, times=2)
    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == 0


def test_one_card_too_many(less_random_state):
    state = less_random_state(start_player=Character.RESEARCHER)

    # cheat and pretend virus is eradicated
    state._players[Character.RESEARCHER]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        City.ATLANTA,
    }

    assert len(state.get_possible_actions()) == 8, state.get_possible_actions()
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))

    state.step(state.get_possible_actions().pop())
    assert state._players[Character.RESEARCHER].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert all(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_two_cards_too_many(less_random_state):
    state = less_random_state()

    # cheat and pretend virus is eradicated
    state._players[Character.SCIENTIST]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        City.ATLANTA,
        City.BAGHDAD,
    }

    assert len(state.get_possible_actions()) == 9, state.get_possible_actions()
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))

    state.step(state.get_possible_actions().pop())
    assert len(state.get_possible_actions()) == 8
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))
    assert state._players[Character.SCIENTIST].num_cards() == 8

    state.step(state.get_possible_actions().pop())
    assert state._players[Character.SCIENTIST].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_one_card_too_many_with_event(less_random_state):
    state = less_random_state()

    # cheat and pretend virus is eradicated
    state._players[Character.SCIENTIST]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        EventCard.ONE_QUIET_NIGHT,
    }

    assert len(state.get_possible_actions()) == 9
    assert all(map(lambda c: isinstance(c, ThrowCard) or isinstance(c, Event), state.get_possible_actions()))

    state.step(state.get_possible_actions().pop())
    assert state._players[Character.SCIENTIST].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_one_card_too_many_with_event_use_event(less_random_state):
    state = less_random_state()

    # cheat and pretend virus is eradicated
    state._players[Character.SCIENTIST]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        EventCard.ONE_QUIET_NIGHT,
    }

    assert len(state.get_possible_actions()) == 9
    assert all(map(lambda c: isinstance(c, ThrowCard) or isinstance(c, Event), state.get_possible_actions()))
    event = OneQuietNight(Character.SCIENTIST)
    assert event in state.get_possible_actions()

    state.step(event)
    assert state._players[Character.SCIENTIST].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_win_condition(less_random_state):
    state = less_random_state(start_player=Character.RESEARCHER)

    state._cures[Virus.BLUE] = True
    state._cures[Virus.BLACK] = True
    state._cures[Virus.YELLOW] = True
    assert state.get_game_condition() == GameState.RUNNING

    state.get_players()[Character.RESEARCHER]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
    }

    cure_action = DiscoverCure(
        target_virus=Virus.RED,
        card_combination=frozenset({City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}),
    )

    assert cure_action in state.get_possible_actions()

    state.step(cure_action)

    assert state.get_game_condition() == GameState.WIN


def test_lose_conditions_no_player_cards(less_random_state):
    state = less_random_state()
    state._player_actions = 1
    state.step(filter_out_events(state.get_possible_actions(), Event).pop())
    state._player_deck = [City.ATLANTA]
    assert state.get_game_condition() == GameState.RUNNING
    assert state.get_phase() == Phase.DRAW_CARDS
    state.step(None)
    assert state.get_game_condition() == GameState.RUNNING
    assert state.get_phase() == Phase.DRAW_CARDS
    state.step(None)
    assert state.get_game_condition() == GameState.LOST
    assert state.get_phase() == Phase.INFECTIONS


def test_lose_conditions_epidemic_counter():
    state = State()
    state._player_actions = 1
    state._phase = Phase.INFECTIONS
    state._infect_city(City.ATLANTA, times=3)
    state._outbreaks = 7
    assert state.get_game_condition() == GameState.RUNNING
    state._infection_deck.insert(0, City.ATLANTA)
    state.step(None)
    assert state._outbreaks >= 8
    assert state.get_game_condition() == GameState.LOST


def test_lose_conditions_no_cubes():
    state = State()
    state._player_actions = 1
    state._phase = Phase.INFECTIONS
    state._infect_city(City.ATLANTA, times=3)
    state._cubes[Virus.BLUE] = 0
    assert state.get_game_condition() == GameState.RUNNING
    state._infection_deck.insert(0, City.ATLANTA)
    state.step(None)
    assert state.get_game_condition() == GameState.LOST


def test_contingency_planner(less_random_state):
    state = less_random_state(start_player=Character.CONTINGENCY_PLANNER)
    active_player = state._active_player
    state._player_discard_pile = [EventCard.ONE_QUIET_NIGHT]

    ability = ReserveCard(EventCard.ONE_QUIET_NIGHT)
    assert ability in state.get_possible_actions()
    state.step(ability)
    assert state._players[active_player].get_contingency_planner_card() == EventCard.ONE_QUIET_NIGHT
    assert EventCard.ONE_QUIET_NIGHT in state.get_player_cards(active_player)

    event = OneQuietNight(player=active_player)
    actions = state.get_possible_actions()
    assert event in actions
    state.step(event)
    assert state._resilient
    assert EventCard.ONE_QUIET_NIGHT not in state.get_player_cards()
    assert state._players[active_player].get_contingency_planner_card() is None
