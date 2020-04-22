from __future__ import division

import time
import math
import random

from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard, DirectFlight


class SpMctsState:
    def is_terminal(self) -> bool:
        raise NotImplementedError

    def take_action(self, action):
        raise NotImplementedError

    def get_reward(self) -> bool:
        raise NotImplementedError

    def get_possible_actions(self):
        raise NotImplementedError


def random_policy(state: SpMctsState):
    while not state.is_terminal():
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.take_action(action)
    return state.get_reward()


def random_filtered_action_policy(state: SpMctsState):
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
        self.squared_reward = 0
        self.children = {}


class SpMcts:
    def __init__(
        self, initial_state: SpMctsState, time_limit=None, iteration_limit=None, exploration_constant=1 / math.sqrt(2), rollout_policy=random_policy, D = 0.1
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
        self.D = D
        self.root: TreeNode = TreeNode(initial_state, None)

    def search(self):
        if self.limit_type == "time":
            time_limit = time.time() + self.time_limit / 1000
            while time.time() < time_limit:
                self.execute_round()
        else:
            [self.execute_round() for i in range(self.search_limit)]

        best_child = self.get_best_child(self.root, 0, self.D)
        return self.get_action(self.root, best_child)

    def execute_round(self):
        node = self.select_node(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def step(self, action):
        self.root = self.root.children[action]
        return self.root.state

    def select_node(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node, self.exploration_constant, self.D)
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
            node.squared_reward += math.pow(reward, 2)
            node = node.parent

    @staticmethod
    def get_best_child(node, exploration_value, D):
        best_value = float("-inf")
        best_nodes = []
        for child in node.children.values():
            node_value = SpMcts.__node_value(child, exploration_value, node, D)
            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)
        return random.choice(best_nodes)

    @staticmethod
    def __node_value(child, exploration_value, node, D):
        return node.state.get_current_player() * child.total_reward / child.num_visits + exploration_value * math.sqrt(
            2 * math.log(node.num_visits) / child.num_visits
        ) + math.sqrt((child.squared_reward - child.num_visits * math.pow(child.squared_reward / child.num_visits, 2) + D) / child.num_visits)

    @staticmethod
    def get_action(root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action
