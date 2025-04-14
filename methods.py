# methods.py (example)
import plane

def random(model):
    """
    Creates one boarding group for all seat rows in the plane.
    If single-door => model.boarding_queue
    If two-doors => decide front/rear queue. 
    """
    id_counter = 1

    # Use model.seat_start_x and model.seat_end_x for row range
    # or (3..(3+29)) directly if you prefer to keep it simple.
    full_group = []
    for x in range(model.seat_start_x, model.seat_end_x + 1):
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(id_counter, model, (x, y), 1)
            id_counter += 1
            full_group.append(agent)

    # Shuffle them
    model.random.shuffle(full_group)

    # Distribute them into queues
    if model.two_doors:
        # For example, half the rows go to front_queue, half to rear_queue
        # Or use a row-based cutoff: row < midpoint => front, row >= midpoint => rear
        # We'll do a naive approach: if x < midpoint => front
        midpoint = (model.seat_start_x + model.seat_end_x) // 2
        for agent in full_group:
            if agent.seat_pos[0] <= midpoint:
                model.front_boarding_queue.append(agent)
            else:
                model.rear_boarding_queue.append(agent)
    else:
        # Single queue
        model.boarding_queue.extend(full_group)



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
    """
    A 6-block, back-to-front boarding strategy:
      - Single door: seat rows are partitioned into 6 blocks from rear (highest x) to front (lowest x), final boarding is strictly back→front.
      - Two doors: same 6-block arrangement, but we:
        1) Do a row-based split around the midpoint (+ offset = -1).
        2) The rear group boards from seat_end down to that midpoint.
        3) The front group boards from that midpoint down to seat_start.
        4) The front group's list is reversed so they effectively go from “middle to front” last.
    """

    seat_start = model.seat_start_x  # typically 3
    seat_end   = model.seat_end_x    # typically 31

    # Build a list of rows in descending order: seat_end..seat_start
    row_list = list(range(seat_end, seat_start - 1, -1))  # e.g. [31..3]
    one_door_list = row_list[::-1]
    n_rows = len(row_list)
    n_blocks = 6

    from math import ceil
    chunk_size = ceil(n_rows / n_blocks)

    blocks = []
    idx = 0
    while idx < n_rows:
        block_rows = one_door_list[idx : idx + chunk_size]
        blocks.append(block_rows)
        idx += chunk_size
        if len(blocks) == n_blocks:
            break

    final_group = []
    pid = 1
    block_id = n_blocks

    # Build final_group in block order (rearmost block first).
    for b_rows in blocks:
        sub_group = []
        for x in b_rows:  # these rows are from rear to front
            for y in (0, 1, 2, 4, 5, 6):
                agent = plane.PassengerAgent(pid, model, (x, y), block_id)
                pid += 1
                sub_group.append(agent)
        model.random.shuffle(sub_group)
        final_group.extend(sub_group)
        block_id -= 1

    # final_group is now from the rearmost block to the frontmost block, back→front.

    if model.two_doors:
        # offset = -1 so that the rearmost row(s) go to front group
        offset = -1
        mid = (seat_start + seat_end) // 2
        limit = mid + offset

        rear_list = []
        front_list = []

        for agent in final_group:
            row_x = agent.seat_pos[0]
            if row_x > limit:
                # rearmost seat
                rear_list.append(agent)
            else:
                front_list.append(agent)

        # Reverse front_list so they board from “middle to front” in order
        rear_list = rear_list[::-1]

        model.rear_boarding_queue.extend(rear_list)
        model.front_boarding_queue.extend(front_list)
    else:
        # Single door: final_group is already strictly back->front
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
    """
    A 'back-to-front' strategy with 15% of agents following a purely random order
    instead of the standard BFS seat order.
      - Single door: merges BFS and random in one final queue
      - Two doors: after partial random assignment, we split by midpoint for front/rear queues
    """
    import random

    seat_start = model.seat_start_x  # e.g., 3
    seat_end   = model.seat_end_x    # e.g., 31

    # We'll keep 85% BFS, 15% random
    random_fraction = 0.15

    # 1) Build a list of all passengers in strict descending row order
    row_list = list(range(seat_end, seat_start - 1, -1))  # e.g. [31..3]
    final_group = []
    pid = 1

    for x in row_list:  # back->front seat rows
        for y in (0, 1, 2, 4, 5, 6):
            agent = plane.PassengerAgent(pid, model, (x, y), group=1)
            pid += 1
            final_group.append(agent)

    # 2) Choose 15% of them to "follow random strategy"
    # i.e., reorder them in a purely random row order
    total_agents = len(final_group)
    rand_count = int(random_fraction * total_agents)
    if rand_count > 0:
        # pick random subset
        rand_indices = random.sample(range(total_agents), rand_count)
        # Extract those agents
        random_agents = [final_group[i] for i in rand_indices]

        # Remove them from BFS group
        for i in sorted(rand_indices, reverse=True):
            del final_group[i]

        # Reassign them seats in random row/column order
        # Approach A: Actually give them random seat positions (swapping with BFS)
        # Approach B: Just reinsert them in random positions within the final queue
        # For example, let's do Approach B:

        random.shuffle(random_agents)  # purely random order
        for agent in random_agents:
            insert_pos = random.randint(0, len(final_group))
            final_group.insert(insert_pos, agent)

    # 3) Reverse final list so that .pop() will yield the highest row first
    #    (assuming your model uses .pop() from the end in the step() method)
    final_group.reverse()

    # 4) For two-door logic, we do midpoint partition
    if model.two_doors:
        midpoint = (seat_start + seat_end) // 2
        rear_list = []
        front_list = []

        for agent in final_group:
            row_x = agent.seat_pos[0]
            if row_x > midpoint:
                rear_list.append(agent)
            else:
                front_list.append(agent)

        # Optionally reverse one or both sub-lists if your .pop() usage needs it
        # e.g., rear_list = list(reversed(rear_list))
        rear_list.reverse()
        model.rear_boarding_queue.extend(rear_list)
        model.front_boarding_queue.extend(front_list)
    else:
        # 1-door scenario
        model.boarding_queue.extend(final_group)

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
    """
    Supports both 1-door and 2-door Steffen Perfect.
      - Single door: rows 3..19 (as before)
      - Two doors: front is rows 3..9, rear is rows 18..10 (skipping row 19).
    """
    if not model.two_doors:
        # ============ SINGLE-DOOR MODE ============
        big_group = []
        id = 1

        # Group 6 seats (rows 3..19, window seats)
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

        model.boarding_queue.extend(big_group)

    else:
        # ============ TWO-DOOR MODE ============
        # Front = rows 3..9
        # Rear  = rows 18..10 (SKIPPING row 19)

        front_big = []
        rear_big = []
        id = 1

        # -------- FRONT BIG (rows 3..9 ascending) --------
        # group 6
        for y in (2, 4):
            for x in range(3, 10, 2):  # 3,5,7,9
                agent = plane.PassengerAgent(id, model, (x, y), 6)
                id += 1
                front_big.append(agent)
        # group 5
        for y in (2, 4):
            for x in range(4, 10, 2):  # 4,6,8
                agent = plane.PassengerAgent(id, model, (x, y), 5)
                id += 1
                front_big.append(agent)
        # group 4
        for y in (1, 5):
            for x in range(3, 10, 2):
                agent = plane.PassengerAgent(id, model, (x, y), 4)
                id += 1
                front_big.append(agent)
        # group 3
        for y in (1, 5):
            for x in range(4, 10, 2):
                agent = plane.PassengerAgent(id, model, (x, y), 3)
                id += 1
                front_big.append(agent)
        # group 2
        for y in (0, 6):
            for x in range(3, 10, 2):
                agent = plane.PassengerAgent(id, model, (x, y), 2)
                id += 1
                front_big.append(agent)
        # group 1
        for y in (0, 6):
            for x in range(4, 10, 2):
                agent = plane.PassengerAgent(id, model, (x, y), 1)
                id += 1
                front_big.append(agent)

        # -------- REAR BIG (rows 18..10 descending) --------
        # SKIP row 19 by starting at 18
        # group 6
        for y in (2, 4):
            for x in range(18, 9, -2):  # 18,16,14,12,10
                agent = plane.PassengerAgent(id, model, (x, y), 6)
                id += 1
                rear_big.append(agent)
        # group 5
        for y in (2, 4):
            for x in range(17, 9, -2):  # 17,15,13,11
                agent = plane.PassengerAgent(id, model, (x, y), 5)
                id += 1
                rear_big.append(agent)
        # group 4
        for y in (1, 5):
            for x in range(18, 9, -2):
                agent = plane.PassengerAgent(id, model, (x, y), 4)
                id += 1
                rear_big.append(agent)
        # group 3
        for y in (1, 5):
            for x in range(17, 9, -2):
                agent = plane.PassengerAgent(id, model, (x, y), 3)
                id += 1
                rear_big.append(agent)
        # group 2
        for y in (0, 6):
            for x in range(18, 9, -2):
                agent = plane.PassengerAgent(id, model, (x, y), 2)
                id += 1
                rear_big.append(agent)
        # group 1
        for y in (0, 6):
            for x in range(17, 9, -2):
                agent = plane.PassengerAgent(id, model, (x, y), 1)
                id += 1
                rear_big.append(agent)

        # Now place front + rear in separate queues, no shuffle
        model.front_boarding_queue.extend(front_big)
        model.rear_boarding_queue.extend(rear_big)


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
