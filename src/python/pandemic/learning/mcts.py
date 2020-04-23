from __future__ import division

import time
import math
import random

from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard, DirectFlight


class MctsState:
    def is_terminal(self) -> bool:
        raise NotImplementedError

    def take_action(self, action):
        raise NotImplementedError

    def get_reward(self) -> bool:
        raise NotImplementedError

    def get_possible_actions(self):
        raise NotImplementedError

    def get_current_player(self):
        raise NotImplementedError


def random_policy(state: MctsState):
    while not state.is_terminal():
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.take_action(action)
    return state.get_reward()


def random_filtered_action_policy(state: MctsState):
    while not state.is_terminal():
        try:
            actions = [
                idx
                for idx, action in enumerate(state._possible_actions)
                if isinstance(action, DriveFerry)
                or isinstance(action, DiscoverCure)
                or isinstance(action, ChooseCard)
                or action == "Wait"
            ]
            if not actions:
                action = random.choice(state.get_possible_actions())
            else:
                action = random.choice(actions)
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        if isinstance(state._possible_actions[action], DirectFlight):
            print(state._possible_actions[action])
        state = state.take_action(action)
    return state.get_reward()


class TreeNode:
    def __init__(self, state, parent):
        self.state = state
        self.is_terminal = state.is_terminal()
        self.is_fully_expanded = self.is_terminal
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.children = {}


class Mcts:
    def __init__(
        self, time_limit=None, iteration_limit=None, exploration_constant=1 / math.sqrt(2), rollout_policy=random_policy
    ):
        if time_limit is not None:
            if iteration_limit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.time_limit = time_limit
            self.limit_type = "time"
        else:
            if iteration_limit is None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iteration_limit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.search_limit = iteration_limit
            self.limit_type = "iterations"
        self.exploration_constant = exploration_constant
        self.rollout = rollout_policy

    def search(self, initial_state):
        self.root = TreeNode(initial_state, None)

        if self.limit_type == "time":
            time_limit = time.time() + self.time_limit / 1000
            while time.time() < time_limit:
                self.execute_round()
        else:
            [self.execute_round() for i in range(self.search_limit)]

        best_child = self.get_best_child(self.root, 0)
        return self.get_action(self.root, best_child)

    def execute_round(self):
        node = self.select_node(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def select_node(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node, self.exploration_constant)
            else:
                return self.expand(node)
        return node

    @staticmethod
    def expand(node):
        actions = node.state.get_possible_actions()
        for action in (a for a in actions if a not in node.children):
            new_node = TreeNode(node.state.take_action(action), node)
            node.children[action] = new_node
            if len(actions) == len(node.children):
                node.is_fully_expanded = True
            return new_node

        raise Exception("Should never reach here")

    @staticmethod
    def backpropogate(node, reward):
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    @staticmethod
    def get_best_child(node, exploration_value):
        best_value = float("-inf")
        best_nodes = []
        nodes_values = {
            node.state._possible_actions[a]: Mcts.__node_value(c, exploration_value, node)
            for a, c in node.children.items()
        }

        for child in node.children.values():
            node_value = Mcts.__node_value(child, exploration_value, node)
            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)
        return random.choice(best_nodes)

    @staticmethod
    def __node_value(child, exploration_value, node):
        return node.state.get_current_player() * child.total_reward / child.num_visits + exploration_value * math.sqrt(
            2 * math.log(node.num_visits) / child.num_visits
        )

    @staticmethod
    def get_action(root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action
