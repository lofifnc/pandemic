from pandemic.learning.mcts import Mcts
from pandemic.learning.mcts_state import PandemicMctsState
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
initial_state = PandemicMctsState(env, easy_state, action_filter=action_filter)
mcts = Mcts(time_limit=5000)
next_state = initial_state
# viz = Visualization(env.state.internal_state)
while not next_state.is_terminal():
    bestAction = mcts.search(initial_state=next_state)
    print(next_state._possible_actions[bestAction])
    next_state = next_state.take_action(bestAction)
    # viz = Visualization(next_state.state)
print(next_state.get_reward())
