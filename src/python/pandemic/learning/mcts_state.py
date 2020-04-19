from copy import deepcopy

from pandemic.learning.environment import PandemicEnvironment
from pandemic.learning.mcts import MctsState
from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation


class PandemicMctsState(MctsState):
    """Returns 1 if it is the maximizer player's turn to choose an action, or -1 for the minimiser player"""

    def get_current_player(self):
        return 1

    def __init__(self, env: Simulation, state, possible_actions=None, done=False, reward=False, phase=1):
        self.env: Simulation = env
        self.state = state
        self._possible_actions = env.get_possible_actions() if possible_actions is None else possible_actions
        self._is_terminal = done
        self._reward = reward
        self.phase = phase

    def is_terminal(self) -> bool:
        return self._is_terminal

    def take_action(self, action):
        action = self._possible_actions[action]
        new_state = deepcopy(self.state)
        self.env.state.internal_state = new_state
        assert action in self._possible_actions
        if action == "Wait":
            self.env.step(None)
        else:
            self.env.step(action)
        actions = self.action_list(self.env.get_possible_actions())
        done = self.env.state.game_state != GameState.RUNNING
        reward = False
        if self.env.state.game_state == GameState.WIN:
            reward = PandemicEnvironment._get_reward(self.env.state.internal_state)
        elif self.env.state.game_state == GameState.LOST:
            calc_reward = PandemicEnvironment._get_reward(self.env.state.internal_state)
            reward = calc_reward if calc_reward else -1

        if any(self.env.state.cures.values()):
            print("found cure !__@_#_@_#_!__@_#arstarst_#)#)#)")
        assert self.state != new_state
        return PandemicMctsState(self.env, self.env.state.internal_state, actions, done, reward, self.env.state.phase)

    def get_reward(self):
        if self.is_terminal():
            return self._reward
        else:
            return False

    def get_possible_actions(self):
        return range(0, len(self._possible_actions))

    @staticmethod
    def action_list(actions):
        if actions is None or actions == []:
            return ["Wait"]
        else:
            return actions


#
# env = Simulation(
#     characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
#     player_deck_shuffle_seed=5,
#     infect_deck_shuffle_seed=10,
#     epidemic_shuffle_seed=12,
# )
#
# initial_state = PandemicMctsState(env, env.state.internal_state)
# mcts = Mcts(time_limit=5000)
# next_state = initial_state
# viz = Visualization(next_state.state)
# while not next_state.is_terminal():
#     bestAction = mcts.search(initial_state=next_state)
#     print(next_state._possible_actions[bestAction])
#     next_state = next_state.take_action(bestAction)
#     viz = Visualization(next_state.state)
# print(next_state.get_reward())
