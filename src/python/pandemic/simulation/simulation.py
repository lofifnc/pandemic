from typing import List, Optional

from pandemic.simulation.actions.events import event_action, get_possible_event_actions
from pandemic.simulation.actions.moves import move_player, get_possible_move_actions
from pandemic.simulation.actions.others import throw_card_action, other_action, get_possible_other_actions
from pandemic.simulation.model.actions import ActionInterface, Movement, Other, Event, DiscardCard, ChooseCard
from pandemic.simulation.model.constants import *
from pandemic.simulation.model.enums import Character, GameState
from pandemic.simulation.model.phases import ChooseCardsPhase, Phase
from pandemic.simulation.state import State


class Simulation:
    def __init__(self, player_count: int = PLAYER_COUNT):
        self.state = State(player_count)

    def step(self, action: Optional[ActionInterface]):
        _state = self.state
        if isinstance(action, DiscardCard):
            throw_card_action(_state, action)
        elif isinstance(action, ChooseCard):
            ccp: ChooseCardsPhase = _state.phase_state
            ccp.add_chosen_card(action.card)
            self.state.phase_state.cards_to_choose_from.remove(action.card)
            if len(ccp.chosen_cards) == ccp.count:
                ccp.call_after(_state)
                _state.phase = ccp.next_phase
        elif isinstance(action, Event):
            event_action(_state, action)

        if _state.phase == Phase.ACTIONS and not isinstance(action, Event):
            self.actions(_state, action)
        elif _state.phase == Phase.DRAW_CARDS:
            _state.draw_cards(action)
        elif _state.phase == Phase.INFECTIONS:
            _state.infections(action)
        elif _state.phase == Phase.EPIDEMIC:
            _state.epidemic_2nd_part()

    @staticmethod
    def actions(state: State, action: ActionInterface):
        if state.actions_left > 0:
            if isinstance(action, Movement):
                move_player(state, action)
            elif isinstance(action, Other):
                other_action(state, action)
            if all(value for value in state.cures.values()):
                state.game_state = GameState.WIN
            state.actions_left -= 1
        if state.actions_left == 0 and state.phase is Phase.ACTIONS:
            state.actions_left = PLAYER_ACTIONS
            state.phase = Phase.DRAW_CARDS

    def get_possible_actions(self, player: Character = None) -> List[ActionInterface]:
        state = self.state

        if player is None:
            player = state.active_player

        possible_actions: List[ActionInterface] = get_possible_event_actions(state)
        if state.phase is Phase.FORECAST or state.phase is Phase.MOVE_STATION:
            return possible_actions

        if state.phase == Phase.CHOOSE_CARDS:
            choose_phase: ChooseCardsPhase = state.phase_state
            return [ChooseCard(choose_phase.player, card) for card in choose_phase.cards_to_choose_from]

        # check all players for hand limit and prompt action
        too_many_cards = False
        extend = possible_actions.extend
        for color, p_state in filter(lambda cs: cs[1].num_cards() > 7, state.players.items()):
            too_many_cards = True
            extend(DiscardCard(color, c) for c in p_state.cards)

        if too_many_cards:
            return possible_actions

        if state.phase is Phase.ACTIONS:
            possible_actions.extend(
                get_possible_move_actions(state, player) + get_possible_other_actions(state, player)
            )
        if state.phase is Phase.DRAW_CARDS:
            return possible_actions
        if state.phase is Phase.INFECTIONS:
            return possible_actions
        return possible_actions

    def reset(self):
        self.state = State()
