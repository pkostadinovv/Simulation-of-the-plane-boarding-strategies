from mesa import Model, Agent
from mesa.space import MultiGrid
import queue_method
import methods
import numpy as np


def baggage_normal():
    """ Generates a positive integer number from normal distribution """
    value = round(np.random.normal(7, 2), 0)
    while value < 0:
        value = round(np.random.normal(7, 2), 0)
    return value


class PassengerAgent(Agent):
    """ An agent with a fixed seat assigned """
    def __init__(self, unique_id, model, seat_pos, group):
        super().__init__(unique_id, model)
        self.seat_pos = seat_pos
        self.group = group
        self.state = 'INACTIVE'
        self.shuffle_dist = 0
        self.shuffle = self.model.shuffle_enable

        # Baggage size logic
        if self.model.common_bags == 'normal':
            self.baggage = baggage_normal()
        else:
            self.baggage = self.model.common_bags

        # NEW: direction attribute, default = +1 (front->back)
        # We'll set it to -1 if passenger is assigned to rear door
        self.direction = 1

    def step(self):
        # Movement logic
        if (self.state == 'GOING'
            and self.model.get_patch((self.pos[0] + (1 * self.direction), self.pos[1])).state == 'FREE'
            and self.model.get_patch((self.pos[0] + (1 * self.direction), self.pos[1])).shuffle == 0):
            if (self.model.get_patch((self.pos[0] + (1 * self.direction), self.pos[1])).back == 0
                or self.model.get_patch((self.pos[0] + (1 * self.direction), self.pos[1])).allow_shuffle is True):
                self.model.get_patch((self.pos[0] + (1 * self.direction), self.pos[1])).allow_shuffle = False
                self.move(1 * self.direction, 0)
                if self.shuffle:
                    if self.pos[0] == self.seat_pos[0]:
                        self.state = 'SHUFFLE CHECK'
                if self.pos[0] == self.seat_pos[0]:
                    if self.baggage > 0:
                        self.state = 'BAGGAGE'
                    else:
                        self.state = 'SEATING'

        elif self.state == 'SHUFFLE':
            # For shuffle, we continue in +1 direction
            if (self.pos[1] == 3 and
                self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).state == 'FREE'):
                if self.pos[0] == self.seat_pos[0]:
                    self.shuffle_dist = self.model.get_patch((self.pos[0], self.pos[1])).shuffle
                    self.model.get_patch((self.pos[0], self.pos[1])).shuffle -= 1
                self.move(self.direction, 0)
                self.shuffle_dist -= 1
                if self.shuffle_dist == 0:
                    self.state = 'BACK'
                    if abs(self.pos[0] - self.seat_pos[0]) == 2:
                        self.model.schedule.safe_remove_priority(self)
                        self.model.schedule.add_priority(self)
            else:
                if (self.pos[1] > 3
                    and self.model.get_patch((self.pos[0], self.pos[1] - 1)).state == 'FREE'):
                    self.move(0, -1)
                elif (self.pos[1] < 3
                      and self.model.get_patch((self.pos[0], self.pos[1] + 1)).state == 'FREE'):
                    self.move(0, 1)

        elif (self.state == 'BACK'
              and self.model.get_patch((self.pos[0] - self.direction, self.pos[1])).state == 'FREE'
              and self.model.get_patch((self.pos[0] - self.direction, self.pos[1])).allow_shuffle is False):
            self.move(-self.direction, 0)
            if self.pos[0] == self.seat_pos[0]:
                self.state = 'SEATING'
                self.model.get_patch((self.pos[0], self.pos[1])).back -= 1
                if self.model.get_patch((self.pos[0], self.pos[1])).back == 0:
                    self.model.get_patch((self.pos[0], self.pos[1])).ongoing_shuffle = False

        elif self.state == 'BAGGAGE':
            if self.baggage > 1:
                self.baggage -= 1
            else:
                self.state = 'SEATING'

        elif self.state == 'SEATING':
            # side movement to seat
            if self.seat_pos[1] in (0, 1, 2):
                self.move(0, -1)
            else:
                self.move(0, 1)
            if self.pos[1] == self.seat_pos[1]:
                self.state = 'FINISHED'
                self.model.schedule.safe_remove(self)
                self.model.schedule.safe_remove_priority(self)

        if (self.state == 'SHUFFLE CHECK'
            and self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).state == 'FREE'
            and self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).ongoing_shuffle == False):
            try:
                shuffle_agents = []
                if self.seat_pos[1] in (0, 1):
                    for y in range(2, self.seat_pos[1], -1):
                        local_agent = self.model.get_passenger((self.seat_pos[0], y))
                        if local_agent is not None and local_agent.state != 'FINISHED':
                            raise Exception()
                        if local_agent is not None:
                            shuffle_agents.append(local_agent)
                elif self.seat_pos[1] in (5, 6):
                    for y in range(4, self.seat_pos[1]):
                        local_agent = self.model.get_passenger((self.seat_pos[0], y))
                        if local_agent is not None and local_agent.state != 'FINISHED':
                            raise Exception()
                        if local_agent is not None:
                            shuffle_agents.append(local_agent)

                shuffle_count = len(shuffle_agents)
                if shuffle_count != 0:
                    self.model.get_patch((self.seat_pos[0], 3)).shuffle = shuffle_count
                    self.model.get_patch((self.seat_pos[0], 3)).back = shuffle_count
                    self.model.get_patch((self.seat_pos[0], 3)).allow_shuffle = True
                    self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).ongoing_shuffle = True
                    for local_agent in shuffle_agents:
                        local_agent.state = 'SHUFFLE'
                        self.model.schedule.safe_remove(local_agent)
                        self.model.schedule.add_priority(local_agent)
                self.state = 'GOING'
            except Exception:
                pass

    def move(self, dx, dy):
        # Clear old cell, move, set new cell
        old_patch = self.model.get_patch((self.pos[0], self.pos[1]))
        old_patch.state = 'FREE'
        self.model.grid.move_agent(self, (self.pos[0] + dx, self.pos[1] + dy))
        new_patch = self.model.get_patch((self.pos[0], self.pos[1]))
        new_patch.state = 'TAKEN'

    def store_luggage(self):
        pass

    def __str__(self):
        return f"ID {self.unique_id}\t: {self.seat_pos}"


class PatchAgent(Agent):
    def __init__(self, unique_id, model, patch_type, state=None):
        super().__init__(unique_id, model)
        self.type = patch_type
        self.state = state
        self.shuffle = 0
        self.back = 0
        self.allow_shuffle = False
        self.ongoing_shuffle = False

    def step(self):
        pass


class PlaneModel(Model):
    """
    A model representing a plane with 16 rows (x=3..18) and 6 seats wide (y=0,1,2,4,5,6).
    corridor at y=3. We support 1 or 2 door boarding, set by 'door_config'.
    If '2 Doors', we create front_boarding_queue and rear_boarding_queue, else single queue.
    """

    method_types = {
        'Random': methods.random,
        'Front-to-back': methods.front_to_back,
        'Front-to-back (4 groups)': methods.front_to_back_gr,
        'Back-to-front': methods.back_to_front,
        'Back-to-front (4 groups)': methods.back_to_front_gr,
        'Window-Middle-Aisle': methods.win_mid_ais,
        'Steffen Perfect': methods.steffen_perfect,
        'Steffen Modified': methods.steffen_modified
    }

    def __init__(self, method, shuffle_enable=True, common_bags='normal', door_config='1 Door'):
        super().__init__()
        self.grid = MultiGrid(21, 7, False)
        self.running = True

        # Custom queue-based scheduler
        self.schedule = queue_method.QueueActivation(self)

        # Store user choices
        self.method_key = method
        self.method = self.method_types[method]
        self.shuffle_enable = shuffle_enable
        self.common_bags = common_bags
        self.two_doors = (door_config == '2 Doors')

        # 2-door logic: if two_doors is True, we use front_boarding_queue & rear_boarding_queue
        # otherwise, single boarding_queue
        if self.two_doors:
            self.front_boarding_queue = []
            self.rear_boarding_queue = []
        else:
            self.boarding_queue = []

        # We'll call the chosen boarding method. That function must decide:
        #  - if two_doors -> put passengers in front or rear queue
        #  - if one_door  -> put all in single queue
        self.method(self)

        # Create patches representing corridor, seats, and walls
        agent_id = 97
        for row in (0, 1, 2, 4, 5, 6):
            for col in (0, 1, 2):
                patch = PatchAgent(agent_id, self, 'WALL')
                self.grid.place_agent(patch, (col, row))
                agent_id += 1
            for col in range(3, 19):
                patch = PatchAgent(agent_id, self, 'SEAT')
                self.grid.place_agent(patch, (col, row))
                agent_id += 1
            for col in (19, 20):
                patch = PatchAgent(agent_id, self, 'WALL')
                self.grid.place_agent(patch, (col, row))
                agent_id += 1

        # Corridor row is at y=3, x from 0..20
        for col in range(21):
            patch = PatchAgent(agent_id, self, 'CORRIDOR', 'FREE')
            self.grid.place_agent(patch, (col, 3))
            agent_id += 1

    def step(self):
        # Step all active agents
        self.schedule.step()

        if not self.two_doors:
            # SINGLE-DOOR logic: front door at (0,3)
            if len(self.grid.get_cell_list_contents((0, 3))) == 1:
                self.get_patch((0, 3)).state = 'FREE'
            if self.get_patch((0, 3)).state == 'FREE' and len(self.boarding_queue) > 0:
                a = self.boarding_queue.pop()
                a.state = 'GOING'
                self.schedule.add(a)
                self.grid.place_agent(a, (0, 3))
                self.get_patch((0, 3)).state = 'TAKEN'
        else:
            # TWO-DOOR logic: front door (0,3), rear door (20,3)

            # front door
            if len(self.grid.get_cell_list_contents((0, 3))) == 1:
                self.get_patch((0, 3)).state = 'FREE'
            if self.get_patch((0, 3)).state == 'FREE' and len(self.front_boarding_queue) > 0:
                front_passenger = self.front_boarding_queue.pop()
                front_passenger.state = 'GOING'
                front_passenger.direction = 1  # moves from x=0 -> x=18
                self.schedule.add(front_passenger)
                self.grid.place_agent(front_passenger, (0, 3))
                self.get_patch((0, 3)).state = 'TAKEN'

            # rear door
            if len(self.grid.get_cell_list_contents((20, 3))) == 1:
                self.get_patch((20, 3)).state = 'FREE'
            if self.get_patch((20, 3)).state == 'FREE' and len(self.rear_boarding_queue) > 0:
                rear_passenger = self.rear_boarding_queue.pop()
                rear_passenger.state = 'GOING'
                rear_passenger.direction = -1  # moves from x=20 -> x=3
                self.schedule.add(rear_passenger)
                self.grid.place_agent(rear_passenger, (20, 3))
                self.get_patch((20, 3)).state = 'TAKEN'

        # End if no more active agents
        if self.schedule.get_agent_count() == 0:
            self.running = False

    def get_patch(self, pos):
        """Return the PatchAgent at pos, if any."""
        agents = self.grid.get_cell_list_contents(pos)
        for agent in agents:
            if isinstance(agent, PatchAgent):
                return agent
        return None

    def get_passenger(self, pos):
        """Return the PassengerAgent at pos, if any."""
        agents = self.grid.get_cell_list_contents(pos)
        for agent in agents:
            if isinstance(agent, PassengerAgent):
                return agent
        return None
