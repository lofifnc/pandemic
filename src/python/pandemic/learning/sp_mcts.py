from __future__ import division

import time
import math
import random
from operator import itemgetter

from pandemic.simulation.model.actions import DriveFerry, DiscoverCure, ChooseCard, DirectFlight
from pandemic.simulation.model.enums import Virus


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
    return state.get_reward(), state.steps


def random_filtered_action_policy(state: SpMctsState, rand):
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
                action = rand.choice(state.get_possible_actions())
            else:
                action = rand.choice(actions)
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        if isinstance(state._possible_actions[action], DirectFlight):
            print(state._possible_actions[action])
        state = state.take_action(action)
    return state.get_reward()


#
# def tabu_filter(color, action):
#     if isinstance(action, DirectFlight):
#         action.player
#
# def tabu_random(state: SpMctsState):
#     color = random.choice(Virus.__colors.keys())
#     while not state.is_terminal():
#         try:
#             actions = [
#                 idx
#                 for idx, action in enumerate(state._possible_actions)
#                 if
#             ]
#             if not actions:
#                 action = random.choice(state.get_possible_actions())
#             else:
#                 action = random.choice(actions)
#         except IndexError:
#             raise Exception("Non-terminal state has no possible actions: " + str(state))
#         if isinstance(state._possible_actions[action], DirectFlight):
#             print(state._possible_actions[action])
#         state = state.take_action(action)
#     return state.get_reward()


class TreeNode:
    def __init__(self, state, parent):
        self.state = state
        self.is_terminal = state.is_terminal()
        self.is_fully_expanded = self.is_terminal
        self.parent = parent
        self.num_visits = 0
        self.total_reward = 0
        self.squared_reward = 0
        self.max_reward = float("-inf")
        self.max_steps = float("inf")
        self.children = {}


class SpMcts:
    def __init__(
        self,
        initial_state: SpMctsState,
        time_limit=None,
        exploration_constant=1 / math.sqrt(2),
        rollout_policy=random_policy,
        D=0.1,
        select_treshold =10,
        meta_time_limit=1000
    ):

        self.search_limit = time_limit
        self.exploration_constant = exploration_constant
        self.rollout = rollout_policy
        self.D = D
        self.root: TreeNode = TreeNode(initial_state, None)
        self.max_reward = float("-inf")
        self.max_steps = 0
        self.select_treshold = select_treshold
        self.meta_time_limit = meta_time_limit

    def search(self):
        meta_search_roots=[]
        root = self.root
        time_limit = time.time() + self.search_limit / 1000
        while time.time() < time_limit:
            meta_search_roots.append(self.meta_search(root, self.meta_time_limit))

        best_root = max(((root, root.max_reward) for root in meta_search_roots), key=itemgetter(1))[0]
        most_rewarding_child = self.get_most_rewarding_child(best_root)
        return self.get_action(self.root, most_rewarding_child)

    def meta_search(self, root, time_limit):
        self.root = root
        executions = 0
        rand = random.Random()

        time_limit = time.time() + time_limit / 1000
        while time.time() < time_limit:
            self.execute_round(rand)
            executions += 1
            if executions % 1000 == 0:
                print("running ", executions, self.max_reward, self.max_steps)

        print(f"meta search ended with max_reward={self.root.max_reward}")
        return self.root

    def execute_round(self, rand):
        node = self.select_node(self.root)
        reward, steps = self.rollout(node.state)
        self.max_reward = max(self.max_reward, reward)
        self.max_steps = max(self.max_steps, steps)

        self.backpropogate(node, reward, steps)

    def get_next_action(self, action):
        self.root = self.root.children[action]
        most_rewarding_child = self.get_most_rewarding_child(self.root)
        return self.get_action(self.root, most_rewarding_child)

    def select_node(self, node):
        if node.num_visits < self.select_treshold:
            return node

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
        nodes_values = ((SpMcts.__node_value(child, exploration_value, node, D), child) for child in node.children.values())
        nodes_viz = {
            node.state._possible_actions[a]: (SpMcts.__node_value(c, exploration_value, node, D), c)
            for a, c in node.children.items()
        }
        best_child = max(nodes_values, key=itemgetter(0))
        return best_child[1]

    @staticmethod
    def get_most_rewarding_child(node):
        return max(((child, child.max_reward) for child in node.children.values()), key=itemgetter(1))[0]
        # @staticmethod
    # def __node_value(child, exploration_value, node, D):
    #     return (
    #         node.state.get_current_player() * child.total_reward / child.num_visits
    #         + exploration_value * math.sqrt(2 * math.log(node.num_visits) / child.num_visits)
    #         + math.sqrt(
    #             (child.squared_reward - child.num_visits * math.pow(child.total_reward / child.num_visits, 2) + D)
    #             / child.num_visits
    #         )
    #     )

    @staticmethod
    def __node_value(child, exploration_value, node, D):
        return (
            node.state.get_current_player() * child.total_reward / child.num_visits
            + exploration_value * math.sqrt(2 * math.log(node.num_visits) / child.num_visits)
            + math.sqrt(
                (child.squared_reward - child.num_visits * math.pow(child.total_reward / child.num_visits, 2) + D)
                / child.num_visits
            )
        )

    # @staticmethod
    # def __node_value(child, exploration_value, node, D):
    #     return child.max_reward / child.max_steps

    @staticmethod
    def get_action(root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action
