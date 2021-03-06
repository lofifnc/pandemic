from copy import deepcopy

from pandemic.simulation.model.actions import (
    Event,
    DiscardCard,
    DiscoverCure,
    ShareKnowledge,
    TreatDisease,
    OneQuietNight,
    ChooseCard,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.enums import Character, Virus, GameState
from pandemic.simulation.simulation import Simulation, Phase, City

from pandemic.test.utils import create_less_random_simulation, filter_out_events, cure_virus


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

        cure_action = DiscoverCure(target_virus=Virus.RED)
        assert cure_action in simulation.get_possible_actions()

        simulation.step(cure_action)
        assert len(simulation.get_possible_actions()) == 5
        cure_virus(
            simulation,
            [City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG],
            Character.RESEARCHER,
        )
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

        assert DiscoverCure(target_virus=Virus.RED) not in simulation.get_possible_actions()

    @staticmethod
    def test_multiple_cure_combinations():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.active_player = Character.RESEARCHER

        cure_cards = [City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG, City.SYDNEY]
        simulation.state.players[Character.RESEARCHER].cards = set(cure_cards).union({EventCard.ONE_QUIET_NIGHT})

        assert DiscoverCure(target_virus=Virus.RED) in simulation.get_possible_actions()

        simulation.step(DiscoverCure(target_virus=Virus.RED))
        actions = simulation.get_possible_actions()
        choices = {ChooseCard(Character.RESEARCHER, card) for card in cure_cards}
        assert choices == set(actions)
        assert len(actions) == len(choices)

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

        TestGeneral.walk_trough_round(simulation)

    @staticmethod
    def test_treat_city_with_cure():
        simulation = create_less_random_simulation()

        # in
        simulation.state.infect_city(City.ATLANTA, times=3)
        simulation.state.cures[Virus.BLUE] = True

        assert simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] == 3
        other = TreatDisease(City.ATLANTA, target_virus=Virus.BLUE)
        assert other in simulation.get_possible_actions()
        simulation.step(other)
        assert simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] == 0

    @staticmethod
    def test_infect_city_with_eradicated_virus():
        simulation = Simulation()

        # cheat and pretend virus is eradicated
        simulation.state.cures[Virus.BLUE] = True
        simulation.state.cubes[Virus.BLUE] = 24
        simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] = 0

        assert simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] == 0
        simulation.state.infect_city(City.ATLANTA, times=2)
        assert simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] == 0

    @staticmethod
    def test_outbreak():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)
        simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] = 3
        before = simulation.state.outbreaks
        assert before == 0
        assert simulation.state.infect_city(City.ATLANTA, times=1)
        assert simulation.state.cities[City.ATLANTA].viral_state[Virus.BLUE] == 3
        assert simulation.state.outbreaks > before

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
        assert all(map(lambda c: isinstance(c, DiscardCard), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.RESEARCHER].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert all(map(lambda c: not isinstance(c, DiscardCard), simulation.get_possible_actions()))

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
        assert all(map(lambda c: isinstance(c, DiscardCard), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert len(simulation.get_possible_actions()) == 8
        assert all(map(lambda c: isinstance(c, DiscardCard), simulation.get_possible_actions()))
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 8

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, DiscardCard), simulation.get_possible_actions()))

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
        assert all(map(lambda c: isinstance(c, DiscardCard) or isinstance(c, Event), simulation.get_possible_actions()))

        simulation.step(simulation.get_possible_actions().pop())
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, DiscardCard), simulation.get_possible_actions()))

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
        assert all(map(lambda c: isinstance(c, DiscardCard) or isinstance(c, Event), simulation.get_possible_actions()))
        event = OneQuietNight(Character.SCIENTIST)
        assert event in simulation.get_possible_actions()

        simulation.step(event)
        assert simulation.state.players[Character.SCIENTIST].num_cards() == 7
        assert len(simulation.get_possible_actions()) > 0
        assert any(map(lambda c: not isinstance(c, DiscardCard), simulation.get_possible_actions()))

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

        cure_action = DiscoverCure(target_virus=Virus.RED)

        assert cure_action in simulation.get_possible_actions()

        simulation.step(cure_action)
        cure_virus(
            simulation,
            [City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA, City.HONG_KONG],
            Character.RESEARCHER,
        )
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
        simulation.state.infect_city(City.ATLANTA, times=3)
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
        simulation.state.infect_city(City.ATLANTA, times=3)
        simulation.state.cubes[Virus.BLUE] = 0
        assert simulation.state.game_state == GameState.RUNNING
        simulation.state.infection_deck.insert(0, City.ATLANTA)
        simulation.step(None)
        assert simulation.state.game_state == GameState.LOST

    @staticmethod
    def test_state_copy():
        simulation = Simulation()

        state_copy = deepcopy(simulation.state.internal_state)
        assert state_copy == simulation.state.internal_state

        TestGeneral.walk_trough_round(simulation)

        assert state_copy != simulation.state.internal_state
        simulation.state.internal_state = state_copy

        TestGeneral.walk_trough_round(simulation)

    @staticmethod
    def test_deterministic_simulation():
        simulation = Simulation(
            characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
            player_deck_shuffle_seed=10,
            infect_deck_shuffle_seed=30,
            epidemic_shuffle_seed=12,
        )
        before_state_copy = deepcopy(simulation.state.internal_state)
        TestGeneral.walk_trough_round(simulation)
        assert before_state_copy != simulation.state.internal_state
        # reset simulation
        after_state_copy = deepcopy(simulation.state.internal_state)
        simulation.state.internal_state = before_state_copy
        TestGeneral.walk_trough_round(simulation)
        assert simulation.state.internal_state == after_state_copy

    @staticmethod
    def walk_trough_round(simulation):
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
    def test_dissect_state_copy():
        simulation = Simulation()

        state = simulation.state.internal_state
        state_copy = deepcopy(simulation.state.internal_state)

        infection_deck_mcopy = state.infection_deck
        assert state_copy.infection_deck == infection_deck_mcopy
        state.infection_deck = []
        assert state_copy.infection_deck != []
        assert state_copy.infection_deck == infection_deck_mcopy

        state.cities[City.ATLANTA].remove_research_station()

        assert state_copy.cities[City.ATLANTA].has_research_station()
        assert not state.cities[City.ATLANTA].has_research_station()

        semi_random_player = list(state.players.keys())[0]
        state.players[semi_random_player].clear_cards()
        assert state.players[semi_random_player].cards != {}
