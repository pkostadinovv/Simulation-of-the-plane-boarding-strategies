import plane

def random(model):
    """ Creates one boarding group, random order. """
    id = 1
    group_front = []
    group_rear = []
    single_group = []

    for x in range(3, 19):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            if model.two_doors:
                # If row >= 10 => rear; else front
                if x >= 10:
                    group_rear.append(agent)
                else:
                    group_front.append(agent)
            else:
                # Single door
                single_group.append(agent)

    if model.two_doors:
        model.random.shuffle(group_front)
        model.random.shuffle(group_rear)
        model.front_boarding_queue.extend(group_front)
        model.rear_boarding_queue.extend(group_rear)
    else:
        model.random.shuffle(single_group)
        model.boarding_queue.extend(single_group)


def front_to_back_gr(model):
    """Front-to-back in 4 groups."""
    final_front_group = []
    final_rear_group = []
    single_queue = []

    id = 1
    final_group = []
    sub_group = []

    # Group 4
    for x in range(18, 14, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 4)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 3
    sub_group = []
    for x in range(14, 10, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 3)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 2
    sub_group = []
    for x in range(10, 6, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 2)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 1
    sub_group = []
    for x in range(6, 2, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Now place into queues
    if model.two_doors:
        for agent in final_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(final_group)
        model.boarding_queue.extend(final_group)


def back_to_front_gr(model):
    """Back-to-front in 4 groups."""
    final_front_group = []
    final_rear_group = []
    single_queue = []

    id = 1
    final_group = []
    sub_group = []

    # Group 4
    for x in range(6, 2, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 4)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 3
    sub_group = []
    for x in range(10, 6, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 3)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 2
    sub_group = []
    for x in range(14, 10, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 2)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    # Group 1
    sub_group = []
    for x in range(18, 14, -1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    final_group.extend(sub_group)

    if model.two_doors:
        for agent in final_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(final_group)
        model.boarding_queue.extend(final_group)


def front_to_back(model):
    final_front_group = []
    final_rear_group = []
    single_queue = []

    group_id = 16
    id = 1
    big_group = []
    for x in range(18,2,-1):
        sub_group = []
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), group_id)
            id += 1
            sub_group.append(agent)
        model.random.shuffle(sub_group)
        big_group.extend(sub_group)
        group_id -= 1

    if model.two_doors:
        for agent in big_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(big_group)
        model.boarding_queue.extend(big_group)


def back_to_front(model):
    final_front_group = []
    final_rear_group = []
    single_queue = []

    group_id = 16
    id = 1
    big_group = []
    for x in range(3, 19):
        sub_group = []
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), group_id)
            id += 1
            sub_group.append(agent)
        model.random.shuffle(sub_group)
        big_group.extend(sub_group)
        group_id -= 1

    if model.two_doors:
        for agent in big_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(big_group)
        model.boarding_queue.extend(big_group)


def win_mid_ais(model):
    final_front_group = []
    final_rear_group = []
    single_queue = []

    id = 1
    big_group = []

    sub_group = []
    for y in (2, 4):
        for x in range(3,19):
            agent = plane.PassengerAgent(id, model, (x, y), 3)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    big_group.extend(sub_group)

    sub_group = []
    for y in (1, 5):
        for x in range(3, 19):
            agent = plane.PassengerAgent(id, model, (x, y), 2)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    big_group.extend(sub_group)

    sub_group = []
    for y in (0, 6):
        for x in range(3,19):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            sub_group.append(agent)
    model.random.shuffle(sub_group)
    big_group.extend(sub_group)

    if model.two_doors:
        # row-based splitting
        for agent in big_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(big_group)
        model.boarding_queue.extend(big_group)


def steffen_perfect(model):
    final_front_group = []
    final_rear_group = []
    single_queue = []

    big_group = []
    id = 1
    # Group 6 seats
    for y in (2, 4):
        for x in range(3, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 6)
            id += 1
            big_group.append(agent)
    # Group 5 seats
    for y in (2, 4):
        for x in range(4, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 5)
            id += 1
            big_group.append(agent)
    # Group 4 seats
    for y in (1, 5):
        for x in range(3, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 4)
            id += 1
            big_group.append(agent)
    # Group 3 seats
    for y in (1, 5):
        for x in range(4, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 3)
            id += 1
            big_group.append(agent)
    # Group 2 seats
    for y in (0, 6):
        for x in range(3, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 2)
            id += 1
            big_group.append(agent)
    # Group 1 seats
    for y in (0, 6):
        for x in range(4, 19, 2):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            big_group.append(agent)

    if model.two_doors:
        for agent in big_group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(big_group)
        model.boarding_queue.extend(big_group)


def steffen_modified(model):
    final_front_group = []
    final_rear_group = []
    single_queue = []

    # For the "modified" approach, let's keep the original grouping
    group = []
    id = 1
    for x in range(3, 19, 2):
        for y in (2, 1, 0):
            agent = plane.PassengerAgent(id, model, (x, y), 4)
            id += 1
            group.append(agent)
    model.random.shuffle(group)

    if model.two_doors:
        for agent in group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
    else:
        single_queue.extend(group)

    group = []
    for x in range(3, 19, 2):
        for y in (4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 3)
            id += 1
            group.append(agent)
    model.random.shuffle(group)

    if model.two_doors:
        for agent in group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
    else:
        single_queue.extend(group)

    group = []
    for x in range(4, 19, 2):
        for y in (2, 1, 0):
            agent = plane.PassengerAgent(id, model, (x, y), 2)
            id += 1
            group.append(agent)
    model.random.shuffle(group)

    if model.two_doors:
        for agent in group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
    else:
        single_queue.extend(group)

    group = []
    for x in range(4, 19, 2):
        for y in (4, 5, 6):
            agent = plane.PassengerAgent(id, model, (x, y), 1)
            id += 1
            group.append(agent)
    model.random.shuffle(group)

    if model.two_doors:
        for agent in group:
            if agent.seat_pos[0] >= 10:
                final_rear_group.append(agent)
            else:
                final_front_group.append(agent)
    else:
        single_queue.extend(group)

    # Now append to the final queues
    if model.two_doors:
        model.random.shuffle(final_front_group)
        model.random.shuffle(final_rear_group)
        model.front_boarding_queue.extend(final_front_group)
        model.rear_boarding_queue.extend(final_rear_group)
    else:
        model.random.shuffle(single_queue)
        model.boarding_queue.extend(single_queue)
