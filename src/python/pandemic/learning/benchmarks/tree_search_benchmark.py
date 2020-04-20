import cProfile
import io
import pstats

from pandemic.learning.mcts_state import PandemicMctsState
from pandemic.learning.tree_search import TreeSearch
from pandemic.simulation.model.enums import Character
from pandemic.simulation.simulation import Simulation


env = Simulation(
    characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
    player_deck_shuffle_seed=5,
    infect_deck_shuffle_seed=10,
    epidemic_shuffle_seed=12,
)

initial_state = PandemicMctsState(env, env.state.internal_state)
tree_search = TreeSearch(step_limit=40000)

pr = cProfile.Profile()
pr.enable()
for _ in range(1, 20000):
    tree_search.search(initial_state=initial_state)


pr.disable()

s = io.StringIO()
sortby = pstats.SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())


