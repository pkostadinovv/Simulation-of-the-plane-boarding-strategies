from mesa import Model, Agent
from mesa.space import MultiGrid
import queue_method
import methods
import numpy as np


def baggage_normal():
    """ Generates a positive integer number from normal distribution """
    value = round(np.random.normal(15, 2), 5)
    while value < 0:
        value = round(np.random.normal(15, 2), 5)
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

        if self.model.common_bags == 'normal':
            self.baggage = baggage_normal()
        else:
            self.baggage = self.model.common_bags

        self.direction = 1

    def step(self):
        if (self.state == 'GOING'
            and self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).state == 'FREE'
            and self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).shuffle == 0):
            if (self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).back == 0
                or self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).allow_shuffle):
                self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).allow_shuffle = False
                self.move(self.direction, 0)
                if self.shuffle and self.pos[0] == self.seat_pos[0]:
                    self.state = 'SHUFFLE CHECK'
                if self.pos[0] == self.seat_pos[0]:
                    self.state = 'BAGGAGE' if self.baggage > 0 else 'SEATING'

        elif self.state == 'SHUFFLE':
            if (self.pos[1] == 3
                and self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).state == 'FREE'):
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
                if self.pos[1] > 3 and self.model.get_patch((self.pos[0], self.pos[1] - 1)).state == 'FREE':
                    self.move(0, -1)
                elif self.pos[1] < 3 and self.model.get_patch((self.pos[0], self.pos[1] + 1)).state == 'FREE':
                    self.move(0, 1)

        elif (self.state == 'BACK'
              and self.model.get_patch((self.pos[0] - self.direction, self.pos[1])).state == 'FREE'
              and not self.model.get_patch((self.pos[0] - self.direction, self.pos[1])).allow_shuffle):
            self.move(-self.direction, 0)
            if self.pos[0] == self.seat_pos[0]:
                self.state = 'SEATING'
                self.model.get_patch((self.pos[0], self.pos[1])).back -= 1
                if self.model.get_patch((self.pos[0], self.pos[1])).back == 0:
                    self.model.get_patch((self.pos[0], self.pos[1])).ongoing_shuffle = False

        elif self.state == 'BAGGAGE':
            self.baggage -= 1
            if self.baggage <= 0:
                self.state = 'SEATING'

        elif self.state == 'SEATING':
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
            and not self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).ongoing_shuffle):
            try:
                shuffle_agents = []
                if self.seat_pos[1] in (0, 1):
                    for y in range(2, self.seat_pos[1], -1):
                        a = self.model.get_passenger((self.seat_pos[0], y))
                        if a and a.state != 'FINISHED': raise Exception()
                        if a: shuffle_agents.append(a)
                elif self.seat_pos[1] in (5, 6):
                    for y in range(4, self.seat_pos[1]):
                        a = self.model.get_passenger((self.seat_pos[0], y))
                        if a and a.state != 'FINISHED': raise Exception()
                        if a: shuffle_agents.append(a)

                if shuffle_agents:
                    self.model.get_patch((self.seat_pos[0], 3)).shuffle = len(shuffle_agents)
                    self.model.get_patch((self.seat_pos[0], 3)).back = len(shuffle_agents)
                    self.model.get_patch((self.seat_pos[0], 3)).allow_shuffle = True
                    self.model.get_patch((self.pos[0] + self.direction, self.pos[1])).ongoing_shuffle = True
                    for a in shuffle_agents:
                        a.state = 'SHUFFLE'
                        self.model.schedule.safe_remove(a)
                        self.model.schedule.add_priority(a)
                self.state = 'GOING'
            except Exception:
                pass

    def move(self, dx, dy):
        old_patch = self.model.get_patch((self.pos[0], self.pos[1]))
        old_patch.state = 'FREE'
        self.model.grid.move_agent(self, (self.pos[0] + dx, self.pos[1] + dy))
        new_patch = self.model.get_patch((self.pos[0], self.pos[1]))
        new_patch.state = 'TAKEN'


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
    method_types = {
        'Random': methods.random,
        'Front-to-back': methods.front_to_back,
        'Front-to-back (4 groups)': methods.front_to_back_gr,
        'Back-to-front': methods.back_to_front,
        'Back-to-front (6 groups)': methods.back_to_front_gr,
        'Window-Middle-Aisle': methods.win_mid_ais,
        'Steffen Perfect': methods.steffen_perfect,
        'Steffen Modified': methods.steffen_modified
    }

    def __init__(self, method, shuffle_enable=True, common_bags='normal', door_config='1 Door'):
        super().__init__()
        self.running = True

        self.num_seat_rows = 29
        self.seat_start_x = 3
        self.seat_end_x = self.seat_start_x + self.num_seat_rows - 1
        self.grid_width = self.seat_end_x + 4
        self.grid = MultiGrid(self.grid_width, 7, False)

        self.schedule = queue_method.QueueActivation(self)
        self.method_key = method
        self.method = self.method_types[method]
        self.shuffle_enable = shuffle_enable
        self.common_bags = common_bags
        self.two_doors = (door_config == '2 Doors')
        self.load_factor=0.8  # New param. Default 80% load factor


        if self.two_doors:
            self.front_boarding_queue = []
            self.rear_boarding_queue = []
        else:
            self.boarding_queue = []

        self.method(self)

        if self.two_doors:
            # FRONT queue
            if self.method_key == "Random":
                self.random.shuffle(self.front_boarding_queue)  # only shuffle if random method
            # preserve seat order if not random; just sub-sample
            keep_front = int(len(self.front_boarding_queue) * self.load_factor)
            indices_front = self.random.sample(range(len(self.front_boarding_queue)), keep_front)
            indices_front.sort()  # so we keep the original seat order
            new_front = [self.front_boarding_queue[i] for i in indices_front]
            self.front_boarding_queue = new_front

            # REAR queue
            if self.method_key == "Random":
                self.random.shuffle(self.rear_boarding_queue)
            keep_rear = int(len(self.rear_boarding_queue) * self.load_factor)
            indices_rear = self.random.sample(range(len(self.rear_boarding_queue)), keep_rear)
            indices_rear.sort()
            new_rear = [self.rear_boarding_queue[i] for i in indices_rear]
            self.rear_boarding_queue = new_rear

        else:
            # Single-door
            if self.method_key == "Random":
                self.random.shuffle(self.boarding_queue)
            keep_count = int(len(self.boarding_queue) * self.load_factor)
            indices = self.random.sample(range(len(self.boarding_queue)), keep_count)
            indices.sort()
            newQ = [self.boarding_queue[i] for i in indices]
            self.boarding_queue = newQ


        agent_id = 97
        for row in (0, 1, 2, 4, 5, 6):
            for col in (0, 1, 2):
                self.grid.place_agent(PatchAgent(agent_id, self, 'WALL'), (col, row))
                agent_id += 1
            for col in range(self.seat_start_x, self.seat_end_x + 1):
                self.grid.place_agent(PatchAgent(agent_id, self, 'SEAT'), (col, row))
                agent_id += 1
            for col in (self.seat_end_x + 1, self.seat_end_x + 2):
                self.grid.place_agent(PatchAgent(agent_id, self, 'WALL'), (col, row))
                agent_id += 1

        for col in range(self.grid_width):
            self.grid.place_agent(PatchAgent(agent_id, self, 'CORRIDOR', 'FREE'), (col, 3))
            agent_id += 1

    def step(self):
        self.schedule.step()
        rear_door_x = self.grid.width - 1

        if not self.two_doors:
            prob_spawn = 0
            if len(self.grid.get_cell_list_contents((0, 3))) == 1:
                self.get_patch((0, 3)).state = 'FREE'
            k = np.random.uniform(0,1)
            if self.get_patch((0, 3)).state == 'FREE' and self.boarding_queue and k>=prob_spawn:
                a = self.boarding_queue.pop()
                a.state = 'GOING'
                self.schedule.add(a)
                self.grid.place_agent(a, (0, 3))
                self.get_patch((0, 3)).state = 'TAKEN'
        else:
            prob_spawn = 1.5
            if len(self.grid.get_cell_list_contents((0, 3))) == 1:
                self.get_patch((0, 3)).state = 'FREE'
            k = np.random.poisson(prob_spawn)
            if self.get_patch((0, 3)).state == 'FREE' and self.front_boarding_queue and k>=1:
                a = self.front_boarding_queue.pop()
                a.state = 'GOING'
                a.direction = 1
                self.schedule.add(a)
                self.grid.place_agent(a, (0, 3))
                self.get_patch((0, 3)).state = 'TAKEN'

            if len(self.grid.get_cell_list_contents((rear_door_x, 3))) == 1:
                self.get_patch((rear_door_x, 3)).state = 'FREE'
            k = np.random.poisson(prob_spawn)
            if self.get_patch((rear_door_x, 3)).state == 'FREE' and self.rear_boarding_queue and k>=1:
                a = self.rear_boarding_queue.pop()
                a.state = 'GOING'
                a.direction = -1
                self.schedule.add(a)
                self.grid.place_agent(a, (rear_door_x, 3))
                self.get_patch((rear_door_x, 3)).state = 'TAKEN'

        if self.schedule.get_agent_count() == 0 and not self.has_more_passengers():
            self.running = False

    def get_patch(self, pos):
        agents = self.grid.get_cell_list_contents(pos)
        for a in agents:
            if isinstance(a, PatchAgent):
                return a
        return None

    def has_more_passengers(self):
        """Return True if there are passengers in any queue."""
        if self.two_doors:
            return (len(self.front_boarding_queue) > 0 or
                    len(self.rear_boarding_queue) > 0)
        else:
            return (len(self.boarding_queue) > 0)

    def get_passenger(self, pos):
        agents = self.grid.get_cell_list_contents(pos)
        for a in agents:
            if isinstance(a, PassengerAgent):
                return a
        return None
