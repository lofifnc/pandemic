from pandemic.learning.mcts import Mcts
from pandemic.learning.mcts_state import PandemicMctsState
from pandemic.learning.sp_mcts import SpMcts
from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard
from pandemic.simulation.model.enums import Character
from pandemic.simulation.simulation import Simulation
from pandemic.learning.easy_mode import easy_state

env = Simulation(
    characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
    player_deck_shuffle_seed=5,
    infect_deck_shuffle_seed=10,
    epidemic_shuffle_seed=12,
)

action_filter = (
    lambda action: isinstance(action, DriveFerry) or isinstance(action, DiscoverCure) or isinstance(action, ChooseCard)
)

env.state.internal_state = easy_state
print(easy_state.active_player)
initial_state = PandemicMctsState(env, easy_state)
mcts = SpMcts(initial_state, time_limit=120000, exploration_constant=0.06, D=0.1)
next_state = initial_state
# viz = Visualization(env.state.internal_state)
bestAction = mcts.search()
next_action = next_state._possible_actions[bestAction]
print(next_action)
next_state = next_state.take_action(bestAction)


while not next_state.is_terminal():
    bestAction = mcts.get_next_action(bestAction)
    next_action = next_state._possible_actions[bestAction]
    print(next_action)
    next_state = next_state.take_action(bestAction)
    # viz = Visualization(next_state.state)
print(next_state.get_reward())
