import pickle

from pandemic.learning.environment import PandemicEnvironment
from pandemic.learning.mcts import MctsState
from pandemic.simulation.model.actions import DirectFlight
from pandemic.simulation.model.enums import GameState
from pandemic.simulation.simulation import Simulation
from pandemic.simulation.state import InternalState


def compute_reward(int_state: InternalState):
    reward = False
    if int_state.game_state == GameState.WIN:
        reward = 4
    elif int_state.game_state == GameState.LOST:
        cure_reward = sum(int_state.cures.values()) * 1
        reward = cure_reward if cure_reward > 0 else 0
    return reward


def compute_ts_reward(int_state: InternalState):
    if int_state.game_state == GameState.WIN:
        return 4
    elif int_state.game_state == GameState.LOST:
        return 0
    else:
        cure_reward = sum(int_state.cures.values()) * 1
        return cure_reward if cure_reward > 0 else False


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
        steps=0,
        reward_function=compute_reward,
    ):
        self.env: Simulation = env
        self.state = pickle.dumps(state)
        self.action_filter = action_filter
        self._possible_actions = (
            self.action_list(env.get_possible_actions()) if possible_actions is None else possible_actions
        )
        self._is_terminal = done
        self._reward = reward
        self.phase = phase
        self.steps = steps
        self.reward_function = reward_function

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
        reward = self.reward_function(self.env.state.internal_state)

        # if any(self.env.state.cures.values()):
        #     print("found cure !__@_#_@_#_!__@_#arstarst_#)#)#) v", self.env.state.cures)
        assert self.state != new_state
        return PandemicMctsState(
            self.env,
            self.env.state.internal_state,
            actions,
            done,
            reward,
            self.env.state.phase,
            self.action_filter,
            self.env.state.internal_state.steps,
            self.reward_function,
        )

    def get_reward(self):
        return self._reward


    def get_possible_actions(self):
        return range(0, len(self._possible_actions))

    def action_list(self, actions):
        if actions is None or actions == []:
            return ["Wait"]
        else:
            filtered_actions = list(filter(self.action_filter, actions))
            return filtered_actions if filtered_actions else actions


class PandemicTreeSearchState(PandemicMctsState):
    def __init__(
        self,
        env: Simulation,
        state,
        possible_actions=None,
        done=False,
        reward=False,
        phase=1,
        action_filter=lambda x: True,
        steps=0,
        reward_function=compute_ts_reward,
    ):
        super().__init__(env, state, possible_actions, done, reward, phase, action_filter, steps, reward_function)
