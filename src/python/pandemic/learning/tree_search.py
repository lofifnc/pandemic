import math
import time
from dataclasses import dataclass
from operator import itemgetter
import random
from typing import Dict, Any

from pandemic.learning.mcts import MctsState


@dataclass
class WalkNode:
    children: Dict[int, Any]
    state: MctsState
    parent: Any
    explored: bool = False
    visited_children: int = 0
    num_visits: int = 0
    total_reward: float = 0
    squared_reward = 0
    max_reward = float("-inf")
    max_steps = float("inf")


class TreeSearch:
    def __init__(
        self, step_limit=None, report_steps=1000, time_limit=None, exploration_constant=1 / math.sqrt(2), D=0.1, select_threshold=1000, next_threshold=100
    ):
        self.max_depth = 0
        self.next_threshold = next_threshold
        self.D = D
        self.exploration_constant = exploration_constant
        self.time_limit = time_limit
        self.root_node: WalkNode = None
        self.discovered_nodes = 0
        self.visited_nodes = 0
        self.discovered_final_states = 0
        self.step_limit = step_limit
        self.max_reward = -100
        self.report_steps = report_steps
        self.steps = 0
        self.current_node = None
        self.select_threshold = select_threshold

    def search(self, initial_state: MctsState):
        self.root_node = WalkNode(dict(), initial_state, None) if self.root_node is None else self.root_node
        self.current_node = self.root_node
        executions = 0

        time_limit = time.time() + self.time_limit / 1000
        while time.time() < time_limit:
            self.walk()
            executions += 1
            if executions % self.report_steps == 0:
                self.print_best_solution()
                print(
                    self.discovered_nodes,
                    self.visited_nodes,
                    self.discovered_final_states,
                    self.max_reward,
                    self.root_node.visited_children,
                    self.max_depth
                )

    def walk(self):
        # if self.step_limit:
        #     condition = lambda s: s < self.step_limit
        # else:
        #     condition = lambda s: True
        reward = self.do_something(self.current_node)
        if self.current_node.num_visits > self.select_threshold:
            if not self.current_node.state.is_terminal():
                print("select new root")
                self.current_node = self.get_best_child(self.current_node, self.exploration_constant, self.D)
            else:
                print("reset to root")
                self.current_node = self.root_node
        return reward

    def do_something(self, start_node):
        current_node = start_node
        current_reward = float("-inf")
        while not current_node.state.is_terminal():
            if current_node.explored:
                if current_node.num_visits > self.select_threshold:
                    current_node = self.get_best_child(current_node, self.exploration_constant, self.D)
                else:
                    action = random.choice(current_node.state.get_possible_actions())
                    current_node = current_node.children[action]
            else:
                if current_node.visited_children == 0:
                    self.discovered_nodes += len(current_node.state.get_possible_actions())
                    reward = current_node.state.get_reward()
                    if reward and current_reward != reward:
                        current_reward = reward
                        reward = reward + 1 / current_node.state.steps
                        self.max_reward = max(self.max_reward, reward)
                        self.backpropogate(current_node, reward, current_node.state.steps)

                try:
                    action = random.choice(current_node.state.get_possible_actions())
                except IndexError:
                    print(current_node.state.state)
                    raise IndexError("blu")
                been_there = current_node.children.get(action, None)
                if been_there:
                    next_node = been_there
                else:
                    next_node = WalkNode(dict(), current_node.state.take_action(action), current_node)
                    current_node.children[action] = next_node
                    current_node.visited_children += 1
                    if current_node.visited_children == len(current_node.state.get_possible_actions()):
                        current_node.explored = True
                current_node = next_node
                self.visited_nodes += 1

        self.discovered_final_states += 1
        reward = current_node.state.get_reward()
        self.max_reward = max(self.max_reward, reward)
        self.backpropogate(current_node, reward, current_node.state.steps)
        self.max_depth = max(self.max_depth, current_node.state.steps)
        return reward

    def print_best_solution(self):
        print("===____ solution ____===")
        node = self.root_node
        while not node.state.is_terminal():
            best_node = self.get_most_rewarding_child(node)
            action = self.get_action(node, best_node)
            print(node.state._possible_actions[action])
            node = best_node
        print("===____ end ____===")

    @staticmethod
    def backpropogate(node, reward, steps):
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node.squared_reward += math.pow(reward, 2)
            if reward >= node.max_reward:
                node.max_reward = reward
                node.max_steps = min(node.max_steps, steps)
            node = node.parent

    @staticmethod
    def get_best_child(node, exploration_value, D):
        nodes_values = (
            (TreeSearch.__node_value(child, exploration_value, node, D), child) for child in node.children.values()
        )
        nodes_viz = {
            node.state._possible_actions[a]: (TreeSearch.__node_value(c, exploration_value, node, D), c)
            for a, c in node.children.items()
        }
        best_child = max(nodes_values, key=itemgetter(0))
        return best_child[1]

    @staticmethod
    def get_most_rewarding_child(node):
        return max(((child, child.max_reward) for child in node.children.values()), key=itemgetter(1))[0]

    @staticmethod
    def __node_value(child, exploration_value, node, D):
        return (
            child.max_reward / child.num_visits
            + exploration_value * math.sqrt(2 * math.log(node.num_visits) / child.num_visits)
            + math.sqrt(
                (child.squared_reward - child.num_visits * math.pow(child.total_reward / child.num_visits, 2) + D)
                / child.num_visits
            )
        )

    @staticmethod
    def get_action(root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action
