from collections import namedtuple
import random

Transition = namedtuple("Transition", ("state", "action", "next_state", "reward"))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def sample_slice(self, slice_size):
        len_memory = len(self.memory)
        start = random.randint(0, slice_size - len_memory)
        return  self.memory[start:start + len_memory]

    def __len__(self):
        return len(self.memory)
