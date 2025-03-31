from mesa.time import BaseScheduler
from collections import OrderedDict
import random

class QueueActivation(BaseScheduler):
    def __init__(self, model):
        super().__init__(model)
        self._priority_agents = OrderedDict()

    def step(self):
        """
        Steps all agents once, but in a randomized order.
        Priority agents get included in the same random shuffle.
        This helps reduce predictable movement artifacts.
        """

        # 1. Gather all agents (priority + regular) into a single list
        all_agents = list(self._priority_agents.values()) + list(self._agents.values())

        # 2. Randomize that list to avoid consistent stepping order
        self.model.random.shuffle(all_agents)

        # 3. Step each agent
        for agent in all_agents:
            # Check if agent still exists in these dicts (it might have been removed)
            if agent.unique_id in self._priority_agents or agent.unique_id in self._agents:
                agent.step()

        # 4. Advance model time
        self.time += 1
        self.steps += 1

    def add_priority(self, agent):
        self._priority_agents[agent.unique_id] = agent

    def remove_priority(self, agent):
        del self._priority_agents[agent.unique_id]

    def safe_remove_priority(self, agent):
        if agent.unique_id in self._priority_agents:
            del self._priority_agents[agent.unique_id]

    def safe_remove(self, agent):
        if agent.unique_id in self._agents:
            del self._agents[agent.unique_id]

    def get_agent_count(self):
        return len(self._agents) + len(self._priority_agents)

    def agent_buffer(self):
        """
        Deprecated in this version:
        We now do a single random shuffle in step().
        If you really need direct iteration, you could still use agent_buffer,
        but it won't randomize or reflect priority properly.
        """
        # We'll keep this method for backward compatibility but won't use it now.
        priority_keys = list(self._priority_agents.keys())
        for key in priority_keys:
            yield self._priority_agents[key]

        agent_keys = list(self._agents.keys())
        for key in agent_keys:
            yield self._agents[key]
