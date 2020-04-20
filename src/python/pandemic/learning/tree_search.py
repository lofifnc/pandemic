from dataclasses import dataclass
from typing import Dict, Any

from pandemic.learning.mcts import MctsState


@dataclass
class WalkNode:
    children: Dict[int, Any]
    state: MctsState
    parent: Any
    explored: bool = False
    visited_children: int = 0


class TreeSearch:
    def __init__(self, step_limit=None, report_steps=1000):
        self.root_node: WalkNode
        self.discovered_nodes = 0
        self.visited_nodes = 0
        self.discovered_final_states = 0
        self.step_limit = step_limit
        self.max_reward = -100
        self.report_steps = report_steps

    def search(self, initial_state: MctsState):
        self.root_node = WalkNode(dict(), initial_state, None)
        self.current_node = self.root_node
        self.walk()

    def walk(self):
        steps = 0
        if self.step_limit:
            condition = lambda s: s < self.step_limit
        else:
            condition = lambda s: True

        while condition(steps):
            self.do_something()
            steps += 1
            if steps % 10000 == 0:
                print(
                    self.discovered_nodes,
                    self.visited_nodes,
                    self.discovered_final_states,
                    self.max_reward,
                    self.root_node.visited_children,
                )

    def do_something(self):
        if self.current_node.state.is_terminal():
            self.discovered_final_states += 1
            self.max_reward = max(self.max_reward, self.current_node.state.get_reward())
            if self.current_node.state.get_reward() > 0:
                print(self.current_node.state.get_reward())
            self.current_node = self.current_node.parent
        elif self.current_node.explored:
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
                self.current_node.children = dict()
            self.current_node = next_node
            self.visited_nodes += 1
