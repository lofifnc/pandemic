import pickle

from pandemic.learning.environment import PandemicEnvironment
from pandemic.learning.mcts import MctsState
from pandemic.simulation.model.actions import DirectFlight
from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation


class PandemicMctsState(MctsState):
    """Returns 1 if it is the maximizer player's turn to choose an action, or -1 for the minimiser player"""

    def get_current_player(self):
        return 1

    def __init__(
        self,
        env: Simulation,
        state,
        possible_actions=None,
        done=False,
        reward=False,
        phase=1,
        action_filter=lambda x: True,
    ):
        self.env: Simulation = env
        self.state = pickle.dumps(state)
        self.action_filter = action_filter
        self._possible_actions = self.action_list(env.get_possible_actions()) if possible_actions is None else possible_actions
        self._is_terminal = done
        self._reward = reward
        self.phase = phase


    def is_terminal(self) -> bool:
        return self._is_terminal

    def take_action(self, action):
        action = self._possible_actions[action]
        new_state = pickle.loads(self.state)
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
            reward = 1
        elif self.env.state.game_state == GameState.LOST:
            reward = -1 - sum(self.env.state.cures.values()) * 0.25

        # if any(self.env.state.cures.values()):
        #     print("found cure !__@_#_@_#_!__@_#arstarst_#)#)#) v", self.env.state.cures)
        assert self.state != new_state
        return PandemicMctsState(
            self.env, self.env.state.internal_state, actions, done, reward, self.env.state.phase, self.action_filter
        )

    def get_reward(self):
        if self.is_terminal():
            return self._reward
        else:
            return False

    def get_possible_actions(self):
        return range(0, len(self._possible_actions))

    def action_list(self, actions):
        if actions is None or actions == []:
            return ["Wait"]
        else:
            filtered_actions = list(filter(self.action_filter, actions))
            actions = filtered_actions if filtered_actions else actions
            if any(filter(lambda a: isinstance(a, DirectFlight), actions)):
                print("hey no!")
            return actions
