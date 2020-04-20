from pandemic.learning.mcts import Mcts
from pandemic.learning.mcts_state import PandemicMctsState
from pandemic.simulation.gui.visualization import Visualization
from pandemic.simulation.model.enums import Character
from pandemic.simulation.simulation import Simulation

env = Simulation(
    characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
    player_deck_shuffle_seed=5,
    infect_deck_shuffle_seed=10,
    epidemic_shuffle_seed=12,
)

initial_state = PandemicMctsState(env, env.state.internal_state)
mcts = Mcts(time_limit=5000)
next_state = initial_state
# viz = Visualization(next_state.state)
while not next_state.is_terminal():
    bestAction = mcts.search(initial_state=next_state)
    print(next_state._possible_actions[bestAction])
    next_state = next_state.take_action(bestAction)
    # viz = Visualization(next_state.state)
print(next_state.get_reward())
