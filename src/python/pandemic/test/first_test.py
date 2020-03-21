from typing import Set, Type

from pandemic.model.actions import Other, Event, ActionInterface, ThrowCard
from pandemic.model.city_id import EventCard
from pandemic.model.enums import PlayerColor, OtherAction, Virus
from pandemic.state import State, Phase, City


def test_cure_virus():
    state = State()

    state.get_players()[PlayerColor.TEAL]._cards = {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA,
                                                    City.HONG_KONG}

    cure_action = Other(
        OtherAction.DISCOVER_CURE,
        City.ATLANTA,
        target_virus=Virus.RED,
        cure_card_combination=frozenset(
            {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
        ),
    )
    assert cure_action in state.get_possible_actions()

    state.step(cure_action)
    assert state._cures[Virus.RED]
    assert not state._cures[Virus.BLUE]
    assert not state._cures[Virus.BLACK]
    assert not state._cures[Virus.YELLOW]
    assert len(state.get_player_cards(PlayerColor.TEAL)) == 0


def test_already_cured_combination():
    state = State()

    state.get_players()[PlayerColor.TEAL]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
    }
    state._cures[Virus.RED] = True

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset(
                {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
            ),
        )
        not in state.get_possible_actions()
    )


def test_multiple_cure_combinations():
    state = State()

    state.get_players()[PlayerColor.TEAL]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
    }

    actions = state.get_possible_actions()

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset(
                (City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.SYDNEY)
            ),
        )
        in actions
    )

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset(
                (City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.HONG_KONG, City.SYDNEY)
            ),
        )
        in actions
    )

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset(
                (City.BANGKOK, City.HO_CHI_MINH_CITY, City.MANILA, City.HONG_KONG, City.SYDNEY)
            ),
        )
        in actions
    )

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset((City.BANGKOK, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY)),
        )
        in actions
    )

    assert (
        Other(
            OtherAction.DISCOVER_CURE,
            City.ATLANTA,
            target_virus=Virus.RED,
            cure_card_combination=frozenset(
                (City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY)
            ),
        )
        in actions
    )


def test_player_change():
    state = State()
    active_player = state._active_player
    assert state.get_next_player() != active_player
    state._active_player = state.get_next_player()
    assert state.get_next_player() == active_player


def test_get_card_sharing():
    state = State()
    active_player = state._active_player
    other_player = state.get_next_player()
    try:
        state._players[other_player].remove_card(City.ATLANTA)
    except KeyError:
        pass
    state._players[other_player].add_card(City.ATLANTA)

    sharing_action = Other(
        OtherAction.SHARE_KNOWLEDGE, City.ATLANTA, card=City.ATLANTA, player=other_player, target_player=active_player
    )

    assert sharing_action in state.get_possible_other_actions()

    state.step(sharing_action)
    assert City.ATLANTA not in state.get_player_cards(other_player)
    assert City.ATLANTA in state.get_player_cards(active_player)

    assert sharing_action not in state.get_possible_other_actions()


def test_give_card_sharing():
    state = State()
    active_player = state._active_player
    other_player = state.get_next_player()
    try:
        state._players[active_player].remove_card(City.ATLANTA)
    except KeyError:
        pass
    state.get_players()[active_player].add_card(City.ATLANTA)

    sharing_action = Other(
        OtherAction.SHARE_KNOWLEDGE, City.ATLANTA, card=City.ATLANTA, player=active_player, target_player=other_player
    )

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

    event = Event(EventCard.ONE_QUIET_NIGHT, player=active_player)
    actions = state.get_possible_actions()
    assert event in actions
    state.step(event)
    assert state._resilient
    assert EventCard.ONE_QUIET_NIGHT not in state.get_player_cards()


def test_treat_city():
    state = State()

    state.get_city(City.ATLANTA).inc_infection()
    virus_count = state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE]
    other = Other(OtherAction.TREAT_DISEASE, City.ATLANTA, target_virus=Virus.BLUE)
    assert other in state.get_possible_actions()
    state.step(other)
    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == virus_count - 1


def test_treat_city_with_cure():
    state = State()

    # in
    state._infect_city(City.ATLANTA, times=3)
    state._cures[Virus.BLUE] = True

    assert state.get_city(City.ATLANTA).get_viral_state()[Virus.BLUE] == 3
    other = Other(OtherAction.TREAT_DISEASE, City.ATLANTA, target_virus=Virus.BLUE)
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


def test_one_card_too_many():
    state = State()

    # cheat and pretend virus is eradicated
    state._players[PlayerColor.TEAL]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        City.ATLANTA
    }
    assert len(state.get_possible_actions()) == 8
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))

    state.step(state.get_possible_actions().pop())
    assert state._players[PlayerColor.TEAL].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert all(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_two_cards_too_many():
    state = State()

    # cheat and pretend virus is eradicated
    state._players[PlayerColor.TEAL]._cards = {
        City.BANGKOK,
        City.HO_CHI_MINH_CITY,
        City.BEIJING,
        City.MANILA,
        City.HONG_KONG,
        City.SYDNEY,
        City.ALGIERS,
        City.ATLANTA,
        City.BAGHDAD
    }

    assert len(state.get_possible_actions()) == 9
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))

    state.step(state.get_possible_actions().pop())
    assert len(state.get_possible_actions()) == 8
    assert all(map(lambda c: isinstance(c, ThrowCard), state.get_possible_actions()))
    assert state._players[PlayerColor.TEAL].num_cards() == 8

    state.step(state.get_possible_actions().pop())
    assert state._players[PlayerColor.TEAL].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_one_card_too_many_with_event():
    state = State()

    # cheat and pretend virus is eradicated
    state._players[PlayerColor.TEAL]._cards = {
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
    assert state._players[PlayerColor.TEAL].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))


def test_one_card_too_many_with_event_use_event():
    state = State()

    # cheat and pretend virus is eradicated
    state._players[PlayerColor.TEAL]._cards = {
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
    event = Event(EventCard.ONE_QUIET_NIGHT, PlayerColor.TEAL)
    assert event in state.get_possible_actions()

    state.step(event)
    assert state._players[PlayerColor.TEAL].num_cards() == 7
    assert len(state.get_possible_actions()) > 0
    assert any(map(lambda c: not isinstance(c, ThrowCard), state.get_possible_actions()))
