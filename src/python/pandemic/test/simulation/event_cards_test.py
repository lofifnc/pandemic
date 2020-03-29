import math
import random

from pandemic.simulation.model.actions import (
    OneQuietNight,
    ResilientPopulation,
    Airlift,
    Forecast,
    GovernmentGrant,
    ForecastOrder,
)
from pandemic.simulation.model.city_id import EventCard, City
from pandemic.simulation.model.enums import Character
from pandemic.simulation.state import State, Phase

from pandemic.simulation.simulation import Simulation
from pandemic.test.simulation.utils import create_less_random_simulation


class TestEventCards:
    @staticmethod
    def test_quiet_event():
        simulation = Simulation()
        active_player = simulation.state.active_player

        simulation.state.players[active_player].add_card(EventCard.ONE_QUIET_NIGHT)

        event = OneQuietNight(player=active_player)
        actions = simulation.get_possible_actions()
        assert event in actions
        simulation.step(event)
        assert simulation.state.one_quiet_night
        assert EventCard.ONE_QUIET_NIGHT not in simulation.state.players[active_player].get_cards()
        simulation.state.phase = Phase.INFECTIONS
        simulation.step(None)
        assert simulation.state.phase == Phase.ACTIONS

    @staticmethod
    def test_resilient_population():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player

        simulation.state.players[active_player].add_card(EventCard.RESILIENT_POPULATION)
        discard_pile_top_card = simulation.state.infection_discard_pile[0]

        event = ResilientPopulation(player=active_player, discard_city=discard_pile_top_card)
        actions = simulation.get_possible_actions()
        assert len(set(simulation.state.infection_discard_pile)) == len(simulation.state.infection_discard_pile)
        assert len(list(filter(lambda a: isinstance(a, ResilientPopulation), actions))) == len(
            simulation.state.infection_discard_pile
        )
        assert event in actions
        simulation.step(event)
        assert discard_pile_top_card not in simulation.state.infection_discard_pile

    @staticmethod
    def test_airlift():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player

        simulation.state.players[active_player].add_card(EventCard.AIRLIFT)

        event = Airlift(player=active_player, target_player=Character.RESEARCHER, destination=City.MANILA)
        actions = simulation.get_possible_actions()
        assert event in actions
        simulation.step(event)
        assert simulation.state.players[Character.RESEARCHER].get_city() == City.MANILA
        assert EventCard.AIRLIFT not in simulation.state.players[active_player].get_cards()
        assert EventCard.AIRLIFT in simulation.state.player_discard_pile

    @staticmethod
    def test_forecast():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player

        simulation.state.players[active_player].add_card(EventCard.FORECAST)

        our_shuffle = simulation.state.infection_deck[:6].copy()
        random.shuffle(our_shuffle)
        event = Forecast(player=active_player)
        actions = simulation.get_possible_actions()
        assert event in actions
        simulation.step(event)
        assert EventCard.FORECAST not in simulation.state.players[active_player].get_cards()
        order = ForecastOrder(active_player, tuple(our_shuffle))
        assert order in simulation.get_possible_actions()
        assert len(list(simulation.get_possible_actions())) == math.factorial(6)
        simulation.step(order)
        assert our_shuffle == simulation.state.infection_deck[:6]

    @staticmethod
    def test_government_grant():
        simulation = create_less_random_simulation()
        active_player = simulation.state.active_player

        simulation.state.players[active_player].add_card(EventCard.GOVERNMENT_GRANT)

        assert not simulation.state.get_city_state(City.BAGHDAD).has_research_station()
        event = GovernmentGrant(player=active_player, target_city=City.BAGHDAD)
        actions = simulation.get_possible_actions()
        assert event in actions
        assert GovernmentGrant(player=active_player, target_city=City.ATLANTA) not in actions
        simulation.step(event)
        assert simulation.state.get_city_state(City.BAGHDAD).has_research_station()
