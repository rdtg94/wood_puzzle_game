# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of BFS algorithm for the game.


#--------------------------------------------

"""
This file implements the Breadth-First Search (BFS) algorithm for solving a game problem. 
It explores the state space level by level to find the shortest path to a goal state, 
defined by diamond collection. The implementation uses a queue for 
state management and tracks explored states to avoid revisiting them. The algorithm 
returns the solution path, the number of nodes explored, and the maximum depth reached 
within a given time limit.
"""

#-----------------------------------------------
#Libraries:

import time
from collections import deque

#------------------------------------------------
def breadth_first_search(initial_state, time_limit):
    """
    This function performs Breadth-First Search (BFS).
    It explores the state space level by level.

    How does it work?
    - Uses a 'queue' (FIFO: First In, First Out).
    - Removes the oldest state from the queue.
    - Generates all its neighbors (states 1 move away).
    - If a neighbor has never been visited, marks it as visited and adds it to the *end* of the queue.
    - Guarantees finding the shortest path in terms of *number of moves*.
    - May use a lot of memory if the 'breadth' of the search tree is large, higher difficulties.

    Returns:
        - path: A list of moves if a solution is found, or [] if not.
        - nodes_explored: How many states were analyzed.
        - max_depth: The maximum depth explored.
    """

    start_time = time.time()

    queue = deque([(initial_state, [])])

    explored = set()

    # Add the initial state as explored/visited.
    initial_key = (tuple(map(tuple, initial_state.board)), tuple(map(tuple, initial_state.current_piece)))
    explored.add(hash(initial_key))

    # Counters for statistics.
    nodes_explored = 0
    max_depth = 0

    while queue and time.time() - start_time < time_limit:
        # Remove the oldest state/path from the *front* of the queue (FIFO).
        state, path = queue.popleft()
        nodes_explored += 1  

        # Check if we've reached the goal (all diamonds collected).
        if state.diamonds_collected >= state.total_diamonds:
            print(f"BFS: Diamond goal reached! Score: {state.score}")
            return path, nodes_explored, len(path)

        current_depth = len(path)
        max_depth = max(max_depth, current_depth)

        # Get all possible moves from the current state.
        possible_moves = state.get_possible_moves()
        if not possible_moves:
            continue

        for move in possible_moves:
            next_state = state.apply_move(move)
            if next_state is None or next_state == state:
                continue

            # Generate the unique key for the next state.
            next_key = (tuple(map(tuple, next_state.board)), tuple(map(tuple, next_state.current_piece)))
            next_hash = hash(next_key)

            # Check if this neighboring state *has not been explored yet*.
            if next_hash not in explored:
                explored.add(next_hash)
                new_path = path + [move]
                queue.append((next_state, new_path))

    print(f"BFS: Time limit reached. Nodes explored: {nodes_explored}, Max depth: {max_depth}")
    return [], nodes_explored, max_depth
