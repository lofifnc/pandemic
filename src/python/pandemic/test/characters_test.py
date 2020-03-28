from pandemic.model.actions import (
    ShareKnowledge,
    BuildResearchStation,
    OperationsFlight,
    DriveFerry,
    ReserveCard,
    OneQuietNight,
    Dispatch,
    TreatDisease,
    DiscoverCure,
)
from pandemic.model.city_id import City, EventCard
from pandemic.model.enums import Character, Virus, GameState
from pandemic.state import Phase

from pandemic.test.utils import create_less_random_state


class TestCharacters:
    @staticmethod
    def test_contingency_planner():
        state = create_less_random_state(start_player=Character.CONTINGENCY_PLANNER)
        active_player = state._active_player
        state._player_discard_pile = [EventCard.ONE_QUIET_NIGHT]

        ability = ReserveCard(EventCard.ONE_QUIET_NIGHT)
        assert ability in state.get_possible_actions()
        state.step(ability)
        assert state._players[active_player].get_contingency_planner_card() == EventCard.ONE_QUIET_NIGHT
        assert EventCard.ONE_QUIET_NIGHT in state.get_player_cards(active_player)
        assert EventCard.ONE_QUIET_NIGHT not in state._player_discard_pile

        event = OneQuietNight(player=active_player)
        actions = state.get_possible_actions()
        assert event in actions
        state.step(event)
        assert state._one_quiet_night
        assert EventCard.ONE_QUIET_NIGHT not in state.get_player_cards()
        assert state._players[active_player].get_contingency_planner_card() is None
        assert EventCard.ONE_QUIET_NIGHT not in state._player_discard_pile

    @staticmethod
    def test_dispatcher():
        state = create_less_random_state(start_player=Character.DISPATCHER)
        active_player = state._active_player
        state._players[active_player].set_city(City.MADRID)

        dispatch_self = Dispatch(active_player, City.ATLANTA)
        assert dispatch_self in state.get_possible_actions()
        move_other_player: DriveFerry = DriveFerry(Character.SCIENTIST, City.WASHINGTON)
        assert move_other_player in state.get_possible_actions()
        assert Dispatch(Character.SCIENTIST, City.MADRID) in state.get_possible_actions()
        state.step(dispatch_self)
        assert state.get_player_current_city(active_player) == City.ATLANTA
        assert move_other_player in state.get_possible_actions()
        state.step(move_other_player)
        assert state.get_player_current_city(Character.SCIENTIST) == City.WASHINGTON

    @staticmethod
    def test_medic():
        state = create_less_random_state(start_player=Character.MEDIC)

        # test treat disease
        state._infect_city(City.ATLANTA, times=3)
        treat = TreatDisease(City.ATLANTA, Virus.BLUE)
        assert treat in state.get_possible_actions()
        state.step(treat)
        assert state.get_city_state(City.ATLANTA).get_viral_state()[Virus.BLUE] == 0

        # test auto treat
        state._infect_city(City.BANGKOK, times=3)
        state.get_city_state(City.BANGKOK).build_research_station()
        assert state.get_city_state(City.BANGKOK).get_viral_state()[Virus.RED] == 3
        state._players[Character.MEDIC].set_city(City.BANGKOK)

        state.get_players()[Character.MEDIC]._cards = {
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
        assert cure_action in state.get_possible_actions()
        state.step(cure_action)
        assert state.get_city_state(City.BANGKOK).get_viral_state()[Virus.RED] == 0

        state._cubes[Virus.RED] = 12
        state._infect_city(City.HO_CHI_MINH_CITY, times=3)
        assert state.get_city_state(City.HO_CHI_MINH_CITY).get_viral_state()[Virus.RED] == 3

        move = DriveFerry(Character.MEDIC, City.HO_CHI_MINH_CITY)
        assert move in state.get_possible_actions()
        state.step(move)
        assert state.get_city_state(City.HO_CHI_MINH_CITY).get_viral_state()[Virus.RED] == 0
        state._infection_deck.insert(0, City.HO_CHI_MINH_CITY)
        state._phase = Phase.INFECTIONS
        state.step(None)
        assert state.get_city_state(City.HO_CHI_MINH_CITY).get_viral_state()[Virus.RED] == 0

    @staticmethod
    def test_operations_export():
        state = create_less_random_state(start_player=Character.OPERATIONS_EXPERT)

        state.get_players()[Character.OPERATIONS_EXPERT]._cards = {City.BANGKOK, City.HO_CHI_MINH_CITY}

        operations_flight = OperationsFlight(Character.OPERATIONS_EXPERT, City.MADRID, discard_card=City.BANGKOK)
        assert operations_flight in state.get_possible_actions()
        state.step(operations_flight)
        assert state.get_player_current_city(Character.OPERATIONS_EXPERT) == City.MADRID
        assert not state.get_players()[Character.OPERATIONS_EXPERT].operations_expert_has_charter_flight()

        build_research_station = BuildResearchStation(City.MADRID)
        assert build_research_station in state.get_possible_actions()
        state.step(build_research_station)
        assert state.get_cities()[City.MADRID].has_research_station()
        assert state.get_players()[Character.OPERATIONS_EXPERT]._cards == {City.HO_CHI_MINH_CITY}
        assert not any(filter(lambda a: isinstance(a, OperationsFlight), state.get_possible_actions()))

    @staticmethod
    def test_quarantine_specialist():
        state = create_less_random_state(start_player=Character.QUARANTINE_SPECIALIST)

        before = state.get_city_state(City.HO_CHI_MINH_CITY).get_viral_state()[Virus.RED]
        outbreaks = state._outbreaks

        state._infection_deck.insert(0, City.HO_CHI_MINH_CITY)
        state._phase = Phase.INFECTIONS
        state.step(None)

        if before < 3:
            assert state.get_city_state(City.HO_CHI_MINH_CITY).get_viral_state()[Virus.RED] == before + 1
        else:
            assert state._outbreaks > outbreaks

        before = state.get_city_state(City.ATLANTA).get_viral_state()[Virus.RED]
        outbreaks = state._outbreaks
        state._infection_deck.insert(0, City.ATLANTA)
        state._phase = Phase.INFECTIONS
        state.step(None)
        assert state.get_city_state(City.ATLANTA).get_viral_state()[Virus.RED] == before
        assert outbreaks == state._outbreaks

        before = state.get_city_state(City.WASHINGTON).get_viral_state()[Virus.RED]
        outbreaks = state._outbreaks
        state._infection_deck.insert(0, City.WASHINGTON)
        state._phase = Phase.INFECTIONS
        state.step(None)
        assert state.get_city_state(City.WASHINGTON).get_viral_state()[Virus.RED] == before
        assert outbreaks == state._outbreaks

    @staticmethod
    def test_researcher():
        state = create_less_random_state(start_player=Character.RESEARCHER)

        state._players[Character.RESEARCHER]._cards = {City.BANGKOK, City.HO_CHI_MINH_CITY}
        share_knowledge = ShareKnowledge(Character.RESEARCHER, City.BANGKOK, Character.SCIENTIST)
        assert share_knowledge in state.get_possible_actions()
        assert (
            ShareKnowledge(Character.RESEARCHER, City.HO_CHI_MINH_CITY, Character.SCIENTIST)
            in state.get_possible_actions()
        )
        state.step(share_knowledge)
        assert state.get_players()[Character.RESEARCHER].get_cards() == {City.HO_CHI_MINH_CITY}
        assert state.get_players()[Character.SCIENTIST].get_cards() == {City.BANGKOK}

        state._active_player = Character.SCIENTIST
        assert share_knowledge not in state.get_possible_actions()
        assert (
            ShareKnowledge(Character.RESEARCHER, City.HO_CHI_MINH_CITY, Character.SCIENTIST)
            in state.get_possible_actions()
        )

    @staticmethod
    def test_scientist():
        state = create_less_random_state(start_player=Character.SCIENTIST)

        state.get_players()[Character.SCIENTIST]._cards = {
            City.BANGKOK,
            City.HO_CHI_MINH_CITY,
            City.BEIJING,
            City.MANILA,
        }

        cure_action = DiscoverCure(
            target_virus=Virus.RED,
            card_combination=frozenset({City.BANGKOK, City.HO_CHI_MINH_CITY, City.BEIJING, City.MANILA}),
        )
        assert cure_action in state.get_possible_actions()

        state.step(cure_action)
        assert state._cures[Virus.RED]
        assert not state._cures[Virus.BLUE]
        assert not state._cures[Virus.BLACK]
        assert not state._cures[Virus.YELLOW]
        assert len(state.get_player_cards(Character.SCIENTIST)) == 0

    @staticmethod
    def test_build_research_station():
        state = create_less_random_state(start_player=Character.SCIENTIST)

        state.get_players()[Character.SCIENTIST]._cards = {City.ATLANTA, City.WASHINGTON, City.NEW_YORK}

        build = BuildResearchStation(city=City.ATLANTA)
        assert build not in state.get_possible_actions()

        state.step(DriveFerry(Character.SCIENTIST, destination=City.WASHINGTON))
        assert not state.get_cities()[City.WASHINGTON].has_research_station()
        build = BuildResearchStation(city=City.WASHINGTON)
        assert build in state.get_possible_actions()
        assert state._research_stations == 5
        state.step(build)
        assert state.get_cities()[City.WASHINGTON].has_research_station()
        assert state.get_players()[Character.SCIENTIST]._cards == {City.ATLANTA, City.NEW_YORK}
        assert state._research_stations == 4
        state._research_stations = 0

        state.step(DriveFerry(Character.SCIENTIST, City.NEW_YORK))
        assert not state.get_cities()[City.NEW_YORK].has_research_station()
        build = BuildResearchStation(city=City.NEW_YORK, move_from=City.ATLANTA)
        assert {build, BuildResearchStation(city=City.NEW_YORK, move_from=City.WASHINGTON)}.issubset(
            state.get_possible_actions()
        )
        state.step(build)
        assert state._research_stations == 0
        assert state.get_cities()[City.NEW_YORK].has_research_station()
        assert not state.get_cities()[City.ATLANTA].has_research_station()
