from pandemic.simulation.model.actions import (
    Event,
    ThrowCard,
    DiscoverCure,
    ShareKnowledge,
    TreatDisease,
    OneQuietNight,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.enums import Character, Virus, GameState
from pandemic.simulation.simulation import Simulation, Phase, City

from pandemic.test.simulation.utils import create_less_random_simulation, filter_out_events


class TestGeneral:
    @staticmethod
    def test_cure_virus():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.players[Character.RESEARCHER]._city_cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
            City.HONG_KONG,
        }

        cure_action = DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset(
                {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
            ),
        )
        assert cure_action in simulation.get_possible_actions()

        simulation.step(cure_action)
        assert simulation.state.cures[Virus.RED]
        assert not simulation.state.cures[Virus.BLUE]
        assert not simulation.state.cures[Virus.BLACK]
        assert not simulation.state.cures[Virus.YELLOW]
        assert len(simulation.state.players[Character.RESEARCHER].cards) == 0

    @staticmethod
    def test_already_cured_combination():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.active_player = Character.RESEARCHER
        simulation.state.players[Character.RESEARCHER]._city_cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
            City.HONG_KONG,
        }
        simulation.state.cures[Virus.RED] = True

        assert (
            DiscoverCure(
                target_virus=Virus.RED,
                card_combination=frozenset(
                    {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
                ),
            )
            not in simulation.get_possible_actions()
        )

    @staticmethod
    def test_multiple_cure_combinations():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.active_player = Character.RESEARCHER
        simulation.state.players[Character.RESEARCHER]._city_cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
            City.HONG_KONG,
            City.SYDNEY,
        }

        actions = simulation.get_possible_actions()

        assert (
            DiscoverCure(
                target_virus=Virus.RED,
                card_combination=frozenset(
                    (City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.SYDNEY)
                ),
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
                card_combination=frozenset(
                    (City.BANGKOK, City.HO_CHI_MINH_CITY, City.MANILA, City.HONG_KONG, City.SYDNEY)
                ),
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
                card_combination=frozenset(
                    (City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY)
                ),
            )
            in actions
        )

    @staticmethod
    def test_player_change():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player
        assert simulation.state.get_next_player() != active_player
        simulation.state.active_player = simulation.state.get_next_player()
        assert simulation.state.get_next_player() == active_player

    @staticmethod
    def test_get_card_sharing():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player
        other_player = simulation.state.get_next_player()
        try:
            simulation.state.players[other_player].remove_card(City.ATLANTA)
        except KeyError:
            pass
        simulation.state.players[other_player].add_card(City.ATLANTA)

        sharing_action = ShareKnowledge(card=City.ATLANTA, player=other_player, target_player=active_player)

        assert sharing_action in simulation.get_possible_actions()

        simulation.step(sharing_action)
        assert City.ATLANTA not in simulation.state.players[other_player].cards
        assert City.ATLANTA in simulation.state.players[active_player].cards

        assert sharing_action not in simulation.get_possible_actions()

    @staticmethod
    def test_give_card_sharing():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player
        other_player = simulation.state.get_next_player()

        simulation.state.players[active_player].add_card(City.ATLANTA)

        sharing_action = ShareKnowledge(card=City.ATLANTA, player=active_player, target_player=other_player)

        assert sharing_action in simulation.get_possible_actions()

        simulation.step(sharing_action)

        assert City.ATLANTA not in simulation.state.players[active_player].cards
        assert City.ATLANTA in simulation.state.players[other_player].cards

        assert sharing_action not in simulation.get_possible_actions()

    @staticmethod
    def test_whole_round():
        simulation = Simulation()

        for i in range(1, 4):
            action = simulation.get_possible_actions()
            assert action != set()
            simulation.step(filter_out_events(action, Event).pop())
            assert simulation.state.phase == Phase.ACTIONS

        action = simulation.get_possible_actions()
        assert action != set()
        simulation.step(filter_out_events(action, Event).pop())
        # draw phase
        assert simulation.state.phase == Phase.DRAW_CARDS

        assert all(isinstance(action, Event) for action in simulation.get_possible_actions())
        simulation.step(None)

        if simulation.state.phase == Phase.EPIDEMIC:
            simulation.step(None)

        assert simulation.state.phase == Phase.DRAW_CARDS
        assert all(isinstance(action, Event) for action in simulation.get_possible_actions())
        simulation.step(None)

        # infection phase
        assert simulation.state.phase == Phase.INFECTIONS

        assert all(isinstance(action, Event) for action in simulation.get_possible_actions())
        simulation.step(None)
        assert simulation.state.phase == Phase.INFECTIONS
        assert all(isinstance(action, Event) for action in simulation.get_possible_actions())
        simulation.step(None)

        # next player
        assert simulation.state.phase == Phase.ACTIONS

    @staticmethod
    def test_treat_city_with_cure():
        simulation = create_less_random_simulation()

        # in
        simulation.state._infect_city(City.ATLANTA, times=3)
        simulation.state.cures[Virus.BLUE] = True

        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] == 3
        other = TreatDisease(City.ATLANTA, target_virus=Virus.BLUE)
        assert other in simulation.get_possible_actions()
        simulation.step(other)
        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] == 0

    @staticmethod
    def test_infect_city_with_eradicated_virus():
        simulation = Simulation()

        # cheat and pretend virus is eradicated
        simulation.state.cures[Virus.BLUE] = True
        simulation.state.cubes[Virus.BLUE] = 24
        simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] = 0

        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] == 0
        simulation.state._infect_city(City.ATLANTA, times=2)
        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] == 0

    @staticmethod
    def test_one_card_too_many():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        # cheat and pretend virus is eradicated
        simulation.state.players[Character.RESEARCHER].cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
            City.HONG_KONG,
            City.SYDNEY,
            City.ALGIERS,
            City.ATLANTA,
        }

        assert len(simulation.get_possible_actions()) == 8, simulation.get_possible_actions()
        assert all(map(lambda c: isinstance(c, ThrowCard), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.RESEARCHER].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert all(map(lambda c: not isinstance(c, ThrowCard), simulation.get_possible_actions()))

    @staticmethod
    def test_two_cards_too_many():
        simulation = create_less_random_simulation()

        # cheat and pretend virus is eradicated
        simulation.state.players[Character.SCIENTIST].cards = {
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

        assert len(simulation.get_possible_actions()) == 9, simulation.get_possible_actions()
        assert all(map(lambda c: isinstance(c, ThrowCard), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert len(simulation.get_possible_actions()) == 8
        assert all(map(lambda c: isinstance(c, ThrowCard), simulation.get_possible_actions()))
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 8

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, ThrowCard), simulation.get_possible_actions()))

    @staticmethod
    def test_one_card_too_many_with_event():
        simulation = create_less_random_simulation()

        # cheat and pretend virus is eradicated
        simulation.state.players[Character.SCIENTIST].add_cards(
            [
                City.BANGKOK,
                City.HO_CHI_MINH_CITY,
                City.BEIJING,
                City.MANILA,
                City.HONG_KONG,
                City.SYDNEY,
                City.ALGIERS,
                EventCard.ONE_QUIET_NIGHT,
            ]
        )

        assert len(simulation.get_possible_actions()) == 9
        assert all(map(lambda c: isinstance(c, ThrowCard) or isinstance(c, Event), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, ThrowCard), simulation.get_possible_actions()))

    @staticmethod
    def test_one_card_too_many_with_event_use_event():
        simulation = create_less_random_simulation()

        # cheat and pretend virus is eradicated
        simulation.state.players[Character.SCIENTIST].add_cards(
            [
                City.BANGKOK,
                City.HO_CHI_MINH_CITY,
                City.BEIJING,
                City.MANILA,
                City.HONG_KONG,
                City.SYDNEY,
                City.ALGIERS,
                EventCard.ONE_QUIET_NIGHT,
            ]
        )

        assert len(simulation.get_possible_actions()) == 9
        assert all(map(lambda c: isinstance(c, ThrowCard) or isinstance(c, Event), simulation.get_possible_actions()))
        event = OneQuietNight(Character.SCIENTIST)
        assert event in simulation.get_possible_actions()

        simulation.step(event)
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, ThrowCard), simulation.get_possible_actions()))

    @staticmethod
    def test_win_condition():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.cures[Virus.BLUE] = True
        simulation.state.cures[Virus.BLACK] = True
        simulation.state.cures[Virus.YELLOW] = True
        assert simulation.state.game_state == GameState.RUNNING

        simulation.state.players[Character.RESEARCHER]._city_cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
            City.HONG_KONG,
        }

        cure_action = DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset(
                {City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG}
            ),
        )

        assert cure_action in simulation.get_possible_actions()

        simulation.step(cure_action)

        assert simulation.state.game_state == GameState.WIN

    @staticmethod
    def test_lose_conditions_no_player_cards():
        simulation = create_less_random_simulation()
        simulation.state.actions_left = 1
        simulation.step(filter_out_events(simulation.get_possible_actions(), Event).pop())
        simulation.state.player_deck = [City.ATLANTA]
        assert simulation.state.game_state == GameState.RUNNING
        assert simulation.state.phase == Phase.DRAW_CARDS
        simulation.step(None)
        assert simulation.state.game_state == GameState.RUNNING
        assert simulation.state.phase == Phase.DRAW_CARDS
        simulation.step(None)
        assert simulation.state.game_state == GameState.LOST
        assert simulation.state.phase == Phase.INFECTIONS

    @staticmethod
    def test_lose_conditions_epidemic_counter():
        simulation = create_less_random_simulation()
        simulation.state.actions_left = 1
        simulation.state.phase = Phase.INFECTIONS
        simulation.state._infect_city(City.ATLANTA, times=3)
        simulation.state.outbreaks = 7
        assert simulation.state.game_state == GameState.RUNNING
        simulation.state.infection_deck.insert(0, City.ATLANTA)
        simulation.step(None)
        assert simulation.state.outbreaks >= 8
        assert simulation.state.game_state == GameState.LOST

    @staticmethod
    def test_lose_conditions_no_cubes():
        simulation = create_less_random_simulation()
        simulation.state.actions_left = 1
        simulation.state.phase = Phase.INFECTIONS
        simulation.state._infect_city(City.ATLANTA, times=3)
        simulation.state.cubes[Virus.BLUE] = 0
        assert simulation.state.game_state == GameState.RUNNING
        simulation.state.infection_deck.insert(0, City.ATLANTA)
        simulation.step(None)
        assert simulation.state.game_state == GameState.LOST
