import itertools
from collections import Counter
from itertools import chain
from typing import List, Set, Optional

from pandemic.simulation.model.actions import (
    ActionInterface,
    Movement,
    Other,
    Event,
    ThrowCard,
    DiscoverCure,
    BuildResearchStation,
    TreatDisease,
    ShareKnowledge,
    ReserveCard,
    ResilientPopulation,
    Airlift,
    Forecast,
    GovernmentGrant,
    OneQuietNight,
    DriveFerry,
    DirectFlight,
    CharterFlight,
    ShuttleFlight,
    Dispatch,
    OperationsFlight,
    ForecastOrder,
)
from pandemic.simulation.model.city_id import EventCard
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.model.playerstate import PlayerState
from pandemic.simulation.state import State, Phase


class Simulation:
    def __init__(self, player_count: int = PLAYER_COUNT):
        self.state = State(player_count)

    def step(self, action: Optional[ActionInterface]):

        if isinstance(action, ThrowCard):
            self.throw_card_action(self.state, action)
        elif isinstance(action, Event):
            self.event_action(self.state, action)

        if self.state.phase == Phase.ACTIONS and not isinstance(action, Event):
            self.actions(self.state, action)
        elif self.state.phase == Phase.DRAW_CARDS:
            self.state.draw_cards(action)
        elif self.state.phase == Phase.INFECTIONS:
            self.state.infections(action)
        elif self.state == Phase.EPIDEMIC:
            self.state.epidemic_2nd_part()

    @staticmethod
    def actions(state: State, action: ActionInterface):
        if state.actions_left > 0:
            if isinstance(action, Movement):
                Simulation.move_player(state, action)
            elif isinstance(action, Other):
                Simulation.other_action(state, action)
            if all(value for value in state.cures.values()):
                state.game_state = GameState.WIN
            state.actions_left -= 1
        if state.actions_left == 0:
            state.actions_left = PLAYER_ACTIONS
            state.phase = Phase.DRAW_CARDS

    def get_possible_actions(self, player: Character = None) -> List[ActionInterface]:
        state = self.state

        if player is None:
            player = state.active_player

        possible_actions: List[ActionInterface] = Simulation.get_possible_event_actions(state)
        if state.phase == Phase.FORECAST:
            return possible_actions

        # check all players for hand limit and prompt action
        too_many_cards = False
        for color, p_state in state.players.items():
            if p_state.num_cards() > 7:
                too_many_cards = True
                possible_actions.extend(ThrowCard(color, c) for c in p_state.get_cards())

        if too_many_cards:
            return possible_actions

        if state.phase == Phase.ACTIONS:
            possible_actions.extend(
                Simulation.get_possible_move_actions(state, player)
                + Simulation.get_possible_other_actions(state, player)
            )
        if state.phase == Phase.DRAW_CARDS:
            return possible_actions
        if state.phase == Phase.INFECTIONS:
            return possible_actions
        return possible_actions

    @staticmethod
    def move_player(state: State, move: Movement):
        destination_city = move.destination
        character = move.player

        if isinstance(move, DriveFerry):
            assert destination_city in state.get_city_state(state.get_player_current_city(character)).get_neighbors()
        if isinstance(move, DirectFlight):
            state.play_card(state.active_player, destination_city)
        if isinstance(move, CharterFlight):
            state.play_card(state.active_player, state.get_player_current_city(character))
        if isinstance(move, ShuttleFlight):
            assert (
                state.get_city_state(state.get_player_current_city(character)).has_research_station()
                and state.get_city_state(destination_city).has_research_station()
            )
        if isinstance(move, OperationsFlight):
            state.play_card(character, move.discard_card)
            state.players[character].used_operations_expert_shuttle_move()

        state.move_player_to_city(character, destination_city)

    @staticmethod
    def other_action(state: State, action: Other, character: Character = None):
        if character is None:
            character = state.active_player

        if isinstance(action, TreatDisease):
            state.treat_city(action.city, action.target_virus, times=1 if character != Character.MEDIC else 3)
        elif isinstance(action, BuildResearchStation):
            if character != Character.OPERATIONS_EXPERT:
                state.play_card(character, action.city)
            state.get_city_state(action.city).build_research_station()
            if action.move_from:
                state.cities[action.move_from].remove_research_station()
            else:
                state.research_stations -= 1
        elif isinstance(action, DiscoverCure):
            for card in action.card_combination:
                state.play_card(character, card)
            state.cures[action.target_virus] = True
            medic = state.players.get(Character.MEDIC, None)
            if medic:
                state.treat_city(medic.get_city(), action.target_virus, 3)
        elif isinstance(action, ShareKnowledge):
            state.play_card(action.player, action.card)
            state.players[action.target_player].add_card(action.card)
        elif isinstance(action, ReserveCard):
            state.player_discard_pile.remove(action.card)
            state.players[character].set_contingency_planner_card(action.card)

    @staticmethod
    def get_possible_move_actions(state: State, character: Character = None) -> List[Movement]:

        if character is None:
            character = state.active_player

        player_state = state.players[character]

        moves = Simulation.__possible_moves(state, character, player_state.get_city_cards())

        # Dispatcher
        if character == Character.DISPATCHER:
            for c in state.players.keys():
                moves.extend(Simulation.__possible_moves(state, c, player_state.get_city_cards()))
            for f, t in itertools.permutations(state.players.keys(), 2):
                moves.append(Dispatch(f, state.get_player_current_city(t)))

            state.players.keys()

        return moves

    @staticmethod
    def __possible_moves(state: State, character: Character, city_cards: Set[City]) -> List[Movement]:
        player_state = state.players[character]
        current_city = player_state.get_city()
        # drives / ferries
        moves: List[Movement] = list(
            map(lambda c: DriveFerry(character, c), state.cities[current_city].get_neighbors())
        )

        # direct flights
        direct_flights = list(DirectFlight(character, c) for c in city_cards if c != current_city)

        # charter flights
        charter_flights: List[Movement] = [
            CharterFlight(character, c)
            for c in (state.cities.keys() if current_city in city_cards else [])
            if c != current_city
        ]
        # shuttle flights between two cities with research station
        shuttle_flights: List[Movement] = list()
        if state.get_city_state(current_city).has_research_station():
            shuttle_flights = list(
                ShuttleFlight(character, cid)
                for cid, loc in state.get_cities().items()
                if loc.has_research_station() and cid != current_city
            )

        # operations expert charter flights
        operation_flights: List[Movement] = list()
        if (
            state.active_player == Character.OPERATIONS_EXPERT
            and state.get_city_state(current_city).has_research_station()
            and player_state.operations_expert_has_charter_flight()
        ):
            for card in player_state.get_city_cards():
                operation_flights.extend(
                    {
                        OperationsFlight(character, destination=c, discard_card=card)
                        for c in state.cities.keys()
                        if c != current_city
                    }
                )

        return moves + direct_flights + charter_flights + shuttle_flights + operation_flights

    @staticmethod
    def get_possible_other_actions(state: State, character: Character = None) -> List[ActionInterface]:
        if character is None:
            character = state.active_player
        else:
            character = character

        player = state.players[character]

        current_city = player.get_city()
        possible_actions: List[ActionInterface] = list()

        # What is treatable?
        for virus, count in state.get_city_state(current_city).get_viral_state().items():
            if count > 0:
                possible_actions.append(TreatDisease(current_city, target_virus=virus))

        # Can I build research station?
        if (
            not state.cities[current_city].has_research_station()
            and current_city in player.get_cards()
            or character == Character.OPERATIONS_EXPERT
        ):
            possible_actions.extend(
                [
                    BuildResearchStation(current_city, move_from=c)
                    for c, s in state.cities.items()
                    if s.has_research_station()
                ]
                if state.research_stations == 0
                else [BuildResearchStation(current_city)]
            )

        # Can I discover a cure at this situation?
        if state.get_city_state(current_city).has_research_station():
            player_card_viruses = [
                state.cities[card].get_color() for card in player.get_cards() if isinstance(card, City)
            ]
            for virus, count in Counter(player_card_viruses).items():
                cards_for_cure = 4 if character == Character.SCIENTIST else 5
                if count >= cards_for_cure and not state.cures[virus]:
                    potential_cure_cards: List[City] = list(
                        filter(lambda c: state.cities[c].get_color() == virus, player.get_city_cards())
                    )

                    for cure_cards in list(itertools.combinations(potential_cure_cards, cards_for_cure)):
                        possible_actions.append(
                            DiscoverCure(target_virus=virus, card_combination=frozenset(cure_cards))
                        )

        # Can I share knowledge?
        players_in_city: Dict[Character, PlayerState] = {
            c: p for c, p in state.players.items() if p.get_city() == current_city
        }
        if len(players_in_city) > 1:
            possible_actions.extend(Simulation._check_oldschool_knowledge_sharing(state, character, players_in_city))
            # Researcher
            researcher = players_in_city.get(Character.RESEARCHER, {})
            for card in researcher and researcher.get_city_cards():
                possible_actions.extend(
                    ShareKnowledge(Character.RESEARCHER, card, target_player=other)
                    for other in players_in_city.keys()
                    if other != character.RESEARCHER
                )

        # Contigency Planner
        if character == Character.CONTINGENCY_PLANNER and not state.players[character].get_contingency_planner_card():
            for card in state.player_discard_pile:
                possible_actions.append(ReserveCard(card))

        return possible_actions

    @staticmethod
    def _check_oldschool_knowledge_sharing(
        state: State, character: Character, players_in_city: Dict[Character, PlayerState]
    ) -> Set[ActionInterface]:
        possible_actions: Set[ActionInterface] = set()
        current_city = state.get_player_current_city(character)
        for c, ps in filter(lambda pst: current_city in pst[1].get_cards(), players_in_city.items()):
            if c == character:
                # give card to other player
                share_with_others = set(
                    ShareKnowledge(card=current_city, player=character, target_player=other)
                    for other in players_in_city.keys()
                    if other != character
                )
                possible_actions = possible_actions.union(share_with_others)
            else:
                # get card from other player
                possible_actions.add(ShareKnowledge(card=current_city, player=c, target_player=character))
        return possible_actions

    @staticmethod
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

    @staticmethod
    def get_forecast_order(state: State) -> List[Event]:
        return [
            ForecastOrder(state.active_player, forecast=tuple(permutation))
            for permutation in itertools.permutations(state.infection_deck[:6])
        ]

    @staticmethod
    def get_possible_event_actions(state: State) -> List[Event]:

        if state.phase == Phase.FORECAST:
            return Simulation.get_forecast_order(state)

        possible_actions: List[Event] = list()
        players_with_event_cards = [(p, s, s.get_event_cards()) for p, s in state.players.items()]
        for player, player_state, event_cards in players_with_event_cards:
            possible_actions.extend(
                chain.from_iterable(
                    Simulation.__action_for_event_card(state, player, card) for card in event_cards
                )
            )

        return possible_actions

    @staticmethod
    def __action_for_event_card(
        state: State, player_color: Character, event_card: EventCard
    ) -> List[Event]:

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

    @staticmethod
    def throw_card_action(state: State, action: ThrowCard):
        assert isinstance(action, ThrowCard)
        state.play_card(action.player, action.card)
