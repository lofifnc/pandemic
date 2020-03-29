import itertools
from collections import Counter
from typing import List, Dict, Set

from pandemic.simulation.model.actions import (
    Other,
    TreatDisease,
    BuildResearchStation,
    DiscoverCure,
    ShareKnowledge,
    ReserveCard,
    ActionInterface,
    ThrowCard,
)
from pandemic.simulation.model.enums import Character
from pandemic.simulation.model.playerstate import PlayerState
from pandemic.simulation.state import State, City


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
        player_card_viruses = [state.cities[card].get_color() for card in player.get_cards() if isinstance(card, City)]
        for virus, count in Counter(player_card_viruses).items():
            cards_for_cure = 4 if character == Character.SCIENTIST else 5
            if count >= cards_for_cure and not state.cures[virus]:
                potential_cure_cards: List[City] = list(
                    filter(lambda c: state.cities[c].get_color() == virus, player.get_city_cards())
                )

                for cure_cards in list(itertools.combinations(potential_cure_cards, cards_for_cure)):
                    possible_actions.append(DiscoverCure(target_virus=virus, card_combination=frozenset(cure_cards)))

    # Can I share knowledge?
    players_in_city: Dict[Character, PlayerState] = {
        c: p for c, p in state.players.items() if p.get_city() == current_city
    }
    if len(players_in_city) > 1:
        possible_actions.extend(__check_oldschool_knowledge_sharing(state, character, players_in_city))
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


def __check_oldschool_knowledge_sharing(
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


def throw_card_action(state: State, action: ThrowCard):
    assert isinstance(action, ThrowCard)
    state.play_card(action.player, action.card)
