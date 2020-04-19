from dataclasses import dataclass
from typing import Dict, Any

from pandemic.learning.mcts import MctsState
from pandemic.learning.mcts_state import PandemicMctsState
from pandemic.simulation.model.enums import Character
from pandemic.simulation.simulation import Simulation


@dataclass
class WalkNode:
    children: Dict[int, Any]
    state: MctsState
    parent: Any
    explored: bool = False
    visited_children: int = 0


class TreeSearch:
    def __init__(self):
        self.root_node: WalkNode
        self.discovered_nodes = 0
        self.visited_nodes = 0

    def search(self, initial_state: MctsState):
        self.root_node = WalkNode(dict(), initial_state, None)
        self.current_node = self.root_node
        self.walk()

    def walk(self):
        steps = 0
        while True:
            self.do_something()
            steps += 1
            if(steps % 1000 == 0):
                print(self.discovered_nodes, self.visited_nodes)

    def do_something(self):
        if self.current_node.state.is_terminal() or self.current_node.explored:
            if self.current_node.state.is_terminal() and self.current_node.state.get_reward() > 0:
                print(self.current_node.state.get_reward())
            self.current_node = self.current_node.parent
        else:
            if self.current_node.visited_children == 0:
                self.discovered_nodes += len(self.current_node.state.get_possible_actions())
            try:
                action = self.current_node.state.get_possible_actions()[self.current_node.visited_children]
                # action = random.choice(
                #     list(
                #         set(current_node.state.get_possible_actions()).difference(set(current_node.children.keys()))
                #     )
                # )

            except IndexError:
                print(self.current_node.state.state)
                raise IndexError("blu")
            next_node = WalkNode(dict(), self.current_node.state.take_action(action), self.current_node)
            self.current_node.children[action] = next_node
            self.current_node.visited_children += 1
            if self.current_node.visited_children == len(self.current_node.state.get_possible_actions()):
                self.current_node.explored = True
            self.current_node = next_node
            self.visited_nodes += 1

#
#
# env = Simulation(
#     characters={Character.RESEARCHER, Character.CONTINGENCY_PLANNER},
#     player_deck_shuffle_seed=5,
#     infect_deck_shuffle_seed=10,
#     epidemic_shuffle_seed=12,
# )
#
# initial_state = PandemicMctsState(env, env.state.internal_state)
# tree_search = TreeSearch()
#
# tree_search.search(initial_state)
