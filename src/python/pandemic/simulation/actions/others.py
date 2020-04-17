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
    DiscardCard,
)
from pandemic.simulation.model.enums import Character, Virus
from pandemic.simulation.model.phases import Phase
from pandemic.simulation.model.playerstate import PlayerState, CITY_DATA
from pandemic.simulation.state import State, City


def other_action(state: State, action: Other, character: Character = None):
    if character is None:
        character = state.active_player

    if isinstance(action, TreatDisease):
        state.treat_city(action.city, action.target_virus, times=1 if character != Character.MEDIC else 3)
    elif isinstance(action, BuildResearchStation):
        if character != Character.OPERATIONS_EXPERT:
            state.play_card(character, action.city)
        build_research_station(state, action.city)
    elif isinstance(action, DiscoverCure):
        state.previous_phase = state.phase
        state.virus_to_cure = action.target_virus
        state.phase = Phase.CURE_VIRUS
    elif isinstance(action, ShareKnowledge):
        state.play_card(action.player, action.card)
        state.players[action.target_player].add_card(action.card)
    elif isinstance(action, ReserveCard):
        state.player_discard_pile.remove(action.card)
        state.players[character].contingency_planner_card = action.card


def get_possible_other_actions(state: State, character: Character = None) -> List[ActionInterface]:
    if character is None:
        character = state.active_player
    else:
        character = character

    player = state.players[character]

    current_city = player.city
    player_cards = player.cards
    current_city_state = state.cities[current_city]
    possible_actions: List[ActionInterface] = list()

    # What is treatable?
    possible_actions.extend(
        TreatDisease(current_city, target_virus=virus)
        for virus, count in current_city_state.viral_state.items()
        if count > 0
    )

    # Can I build research station?
    if (
        not current_city_state.has_research_station()
        and current_city in player_cards
        or character == Character.OPERATIONS_EXPERT
    ):
        possible_actions.append(BuildResearchStation(current_city))

    # Can I discover a cure at this situation?
    cards_for_cure = num_cards_for_cure(character)
    player_city_cards = player.city_cards
    if current_city_state.has_research_station() and len(player_city_cards) >= cards_for_cure:
        player_card_viruses = [CITY_DATA[card].color for card in player.city_cards]
        append = possible_actions.append
        for virus, count in Counter(player_card_viruses).items():
            if count >= cards_for_cure and not state.cures[virus]:
                append(DiscoverCure(target_virus=virus))
                break

    # Can I share knowledge?
    players_in_city: Dict[Character, PlayerState] = {c: p for c, p in state.players.items() if p.city == current_city}
    if len(players_in_city) > 1:
        possible_actions.extend(__check_oldschool_knowledge_sharing(state, character, players_in_city))
        # Researcher
        researcher = players_in_city.get(Character.RESEARCHER, {})
        if researcher:
            possible_actions.extend(
                ShareKnowledge(Character.RESEARCHER, card, target_player=other)
                for other, card in itertools.product(
                    (other for other in players_in_city.keys() if other != Character.RESEARCHER), researcher.city_cards
                )
            )

    # Contigency Planner
    if character == Character.CONTINGENCY_PLANNER and not state.players[character].contingency_planner_card:
        possible_actions.extend(ReserveCard(card) for card in state.player_discard_pile)

    return possible_actions


def num_cards_for_cure(character):
    return 4 if character == Character.SCIENTIST else 5


def __potential_cure_cards(state: State, virus: Virus, city_cards=List[City]) -> List[City]:
    return list(filter(lambda c: state.cities[c].color == virus, city_cards))


def __check_oldschool_knowledge_sharing(
    state: State, character: Character, players_in_city: Dict[Character, PlayerState]
) -> List[ActionInterface]:
    possible_actions: List[ActionInterface] = list()
    current_city = state.get_player_current_city(character)
    for c, ps in filter(lambda pst: current_city in pst[1].cards, players_in_city.items()):
        __add_knowlegde_sharing(c, character, current_city, players_in_city, possible_actions)
    return possible_actions


def __add_knowlegde_sharing(character, current_character, current_city, players_in_city, possible_actions):
    if character == current_character:
        # give card to other player
        share_with_others = list(
            ShareKnowledge(card=current_city, player=current_character, target_player=other)
            for other in players_in_city.keys()
            if other != current_character
        )
        possible_actions.extend(share_with_others)
    else:
        # get card from other player
        possible_actions.append(ShareKnowledge(card=current_city, player=character, target_player=current_character))


def throw_card_action(state: State, action: DiscardCard):
    assert isinstance(action, DiscardCard)
    state.play_card(action.player, action.card)


def build_research_station(state: State, city: City):
    if state.research_stations == 0:
        state.previous_phase = state.phase
        state.phase = Phase.MOVE_STATION
    else:
        state.research_stations -= 1
    state.cities[city].build_research_station()
    state.last_build_research_station = city
