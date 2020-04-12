from typing import List

from pandemic.simulation.model.actions import (
    ShareKnowledge,
    BuildResearchStation,
    OperationsFlight,
    DriveFerry,
    ReserveCard,
    OneQuietNight,
    Dispatch,
    TreatDisease,
    DiscoverCure,
    MoveResearchStation,
    ChooseCard,
)
from pandemic.simulation.model.city_id import City, EventCard
from pandemic.simulation.model.enums import Character, Virus
from pandemic.simulation.simulation import Phase, Simulation

from pandemic.test.utils import create_less_random_simulation, cure_virus


class TestCharacters:
    @staticmethod
    def test_contingency_planner():
        simulation = create_less_random_simulation(start_player=Character.CONTINGENCY_PLANNER)
        active_player = simulation.state.active_player
        simulation.state.player_discard_pile = [EventCard.ONE_QUIET_NIGHT]

        ability = ReserveCard(EventCard.ONE_QUIET_NIGHT)
        assert ability in simulation.get_possible_actions()
        simulation.step(ability)
        assert simulation.state.players[active_player].contingency_planner_card == EventCard.ONE_QUIET_NIGHT
        assert EventCard.ONE_QUIET_NIGHT in simulation.state.players[active_player].cards
        assert EventCard.ONE_QUIET_NIGHT not in simulation.state.player_discard_pile

        event = OneQuietNight(player=active_player)
        actions = simulation.get_possible_actions()
        assert event in actions
        simulation.step(event)
        assert simulation.state.one_quiet_night
        assert EventCard.ONE_QUIET_NIGHT not in simulation.state.players[active_player].cards
        assert simulation.state.players[active_player].contingency_planner_card is None
        assert EventCard.ONE_QUIET_NIGHT not in simulation.state.player_discard_pile

    @staticmethod
    def test_dispatcher():
        simulation = create_less_random_simulation(start_player=Character.DISPATCHER)
        active_player = simulation.state.active_player
        simulation.state.players[active_player].city = City.MADRID

        dispatch_self = Dispatch(active_player, City.ATLANTA)
        assert dispatch_self in simulation.get_possible_actions()
        move_other_player: DriveFerry = DriveFerry(Character.SCIENTIST, City.WASHINGTON)
        assert move_other_player in simulation.get_possible_actions()
        assert Dispatch(Character.SCIENTIST, City.MADRID) in simulation.get_possible_actions()
        simulation.step(dispatch_self)
        assert simulation.state.players[active_player].city == City.ATLANTA
        assert move_other_player in simulation.get_possible_actions()
        simulation.step(move_other_player)
        assert simulation.state.players[Character.SCIENTIST].city == City.WASHINGTON

    @staticmethod
    def test_medic():
        simulation = create_less_random_simulation(start_player=Character.MEDIC)

        # test treat disease
        simulation.state.infect_city(City.ATLANTA, times=3)
        treat = TreatDisease(City.ATLANTA, Virus.BLUE)
        assert treat in simulation.get_possible_actions()
        simulation.step(treat)
        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.BLUE] == 0

        # test auto treat
        simulation.state.infect_city(City.BANGKOK, times=3)
        simulation.state.cities[City.BANGKOK].build_research_station()
        assert simulation.state.cities[City.BANGKOK].get_viral_state()[Virus.RED] == 3
        simulation.state.players[Character.MEDIC].city = City.BANGKOK

        simulation.state.players[Character.MEDIC]._city_cards = {
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
            Character.MEDIC,
        )
        assert simulation.state.cities[City.BANGKOK].get_viral_state()[Virus.RED] == 0

        simulation.state.cubes[Virus.RED] = 12
        simulation.state.infect_city(City.HO_CHI_MINH_CITY, times=3)
        assert simulation.state.cities[City.HO_CHI_MINH_CITY].get_viral_state()[Virus.RED] == 3

        move = DriveFerry(Character.MEDIC, City.HO_CHI_MINH_CITY)
        assert move in simulation.get_possible_actions()
        simulation.step(move)
        assert simulation.state.cities[City.HO_CHI_MINH_CITY].get_viral_state()[Virus.RED] == 0
        simulation.state.infection_deck.insert(0, City.HO_CHI_MINH_CITY)
        simulation.state.phase = Phase.INFECTIONS
        simulation.step(None)
        assert simulation.state.cities[City.HO_CHI_MINH_CITY].get_viral_state()[Virus.RED] == 0

    @staticmethod
    def test_operations_export():
        simulation = create_less_random_simulation(start_player=Character.OPERATIONS_EXPERT)

        simulation.state.players[Character.OPERATIONS_EXPERT]._city_cards = {City.BANGKOK, City.HO_CHI_MINH_CITY}

        operations_flight = OperationsFlight(Character.OPERATIONS_EXPERT, City.MADRID, discard_card=City.BANGKOK)
        assert operations_flight in simulation.get_possible_actions()
        simulation.step(operations_flight)
        assert simulation.state.players[Character.OPERATIONS_EXPERT].city == City.MADRID
        assert not simulation.state.players[Character.OPERATIONS_EXPERT].operations_expert_has_charter_flight()

        build_research_station = BuildResearchStation(City.MADRID)
        assert build_research_station in simulation.get_possible_actions()
        simulation.step(build_research_station)
        assert simulation.state.cities[City.MADRID].has_research_station()
        assert simulation.state.players[Character.OPERATIONS_EXPERT]._city_cards == {City.HO_CHI_MINH_CITY}
        assert not any(filter(lambda a: isinstance(a, OperationsFlight), simulation.get_possible_actions()))

    @staticmethod
    def test_quarantine_specialist():
        simulation = create_less_random_simulation(start_player=Character.QUARANTINE_SPECIALIST)

        before = simulation.state.cities[City.HO_CHI_MINH_CITY].get_viral_state()[Virus.RED]
        outbreaks = simulation.state.outbreaks

        simulation.state.infection_deck.insert(0, City.HO_CHI_MINH_CITY)
        simulation.state.phase = Phase.INFECTIONS
        simulation.step(None)

        if before < 3:
            assert simulation.state.cities[City.HO_CHI_MINH_CITY].get_viral_state()[Virus.RED] == before + 1
        else:
            assert simulation.state.outbreaks > outbreaks

        before = simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.RED]
        outbreaks = simulation.state.outbreaks
        simulation.state.infection_deck.insert(0, City.ATLANTA)
        simulation.state.phase = Phase.INFECTIONS
        simulation.step(None)
        assert simulation.state.cities[City.ATLANTA].get_viral_state()[Virus.RED] == before
        assert outbreaks == simulation.state.outbreaks

        before = simulation.state.cities[City.WASHINGTON].get_viral_state()[Virus.RED]
        outbreaks = simulation.state.outbreaks
        simulation.state.infection_deck.insert(0, City.WASHINGTON)
        simulation.state.phase = Phase.INFECTIONS
        simulation.step(None)
        assert simulation.state.cities[City.WASHINGTON].get_viral_state()[Virus.RED] == before
        assert outbreaks == simulation.state.outbreaks

    @staticmethod
    def test_researcher():
        simulation = create_less_random_simulation(start_player=Character.RESEARCHER)

        simulation.state.players[Character.RESEARCHER]._city_cards = {City.BANGKOK, City.HO_CHI_MINH_CITY}
        share_knowledge = ShareKnowledge(Character.RESEARCHER, City.BANGKOK, Character.SCIENTIST)
        assert share_knowledge in simulation.get_possible_actions()
        assert (
            ShareKnowledge(Character.RESEARCHER, City.HO_CHI_MINH_CITY, Character.SCIENTIST)
            in simulation.get_possible_actions()
        )
        simulation.step(share_knowledge)
        assert simulation.state.players[Character.RESEARCHER].cards == {City.HO_CHI_MINH_CITY}
        assert simulation.state.players[Character.SCIENTIST].cards == {City.BANGKOK}

        simulation.state.active_player = Character.SCIENTIST
        assert share_knowledge not in simulation.get_possible_actions()
        assert (
            ShareKnowledge(Character.RESEARCHER, City.HO_CHI_MINH_CITY, Character.SCIENTIST)
            in simulation.get_possible_actions()
        )

    @staticmethod
    def test_scientist():
        simulation = create_less_random_simulation(start_player=Character.SCIENTIST)

        simulation.state.players[Character.SCIENTIST]._city_cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
        }

        cure_action = DiscoverCure(target_virus=Virus.RED)
        assert cure_action in simulation.get_possible_actions()
        simulation.step(cure_action)
        cure_virus(simulation, [City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA], Character.SCIENTIST)
        assert simulation.state.cures[Virus.RED]
        assert not simulation.state.cures[Virus.BLUE]
        assert not simulation.state.cures[Virus.BLACK]
        assert not simulation.state.cures[Virus.YELLOW]
        assert len(simulation.state.players[Character.SCIENTIST].cards) == 0

    @staticmethod
    def test_build_research_station():
        simulation = create_less_random_simulation(start_player=Character.SCIENTIST)

        simulation.state.players[Character.SCIENTIST]._city_cards = {City.ATLANTA, City.WASHINGTON, City.NEW_YORK}

        build = BuildResearchStation(city=City.ATLANTA)
        assert build not in simulation.get_possible_actions()

        simulation.step(DriveFerry(Character.SCIENTIST, destination=City.WASHINGTON))
        assert not simulation.state.cities[City.WASHINGTON].has_research_station()
        build = BuildResearchStation(city=City.WASHINGTON)
        assert build in simulation.get_possible_actions()
        assert simulation.state.research_stations == 5
        simulation.step(build)
        assert simulation.state.cities[City.WASHINGTON].has_research_station()
        assert simulation.state.players[Character.SCIENTIST]._city_cards == {City.ATLANTA, City.NEW_YORK}
        assert simulation.state.research_stations == 4
        simulation.state.research_stations = 0

        simulation.step(DriveFerry(Character.SCIENTIST, City.NEW_YORK))
        assert not simulation.state.cities[City.NEW_YORK].has_research_station()
        build = BuildResearchStation(city=City.NEW_YORK)
        simulation.step(build)

        move_station = MoveResearchStation(Character.SCIENTIST, City.ATLANTA)
        assert set([MoveResearchStation(Character.SCIENTIST, City.WASHINGTON), move_station]) == set(simulation.get_possible_actions())

        simulation.step(move_station)

        assert simulation.state.research_stations == 0
        assert simulation.state.cities[City.NEW_YORK].has_research_station()
        assert not simulation.state.cities[City.ATLANTA].has_research_station()
        assert simulation.state.phase == Phase.ACTIONS
