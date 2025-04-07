# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of DFS algorithm for the game.

#--------------------------------------------

"""
This file implements the Depth-First Search (DFS) algorithm for solving a game problem.
It explores the state space by going as deep as possible along a branch before backtracking.
The algorithm uses a stack for state management and tracks explored states to avoid revisiting them.
It does not guarantee the shortest path but can be memory-efficient compared to BFS.

Returns:
- path: A list of moves if a solution is found, or [] if not.
- nodes_explored: How many states were analyzed.
- max_depth: The maximum depth explored.
"""

#-----------------------------------------------
# Libraries:

import time

#------------------------------------------------
def depth_first_search(initial_state, time_limit):
    """
    This function performs Depth-First Search (DFS).
    It explores the state space by going as deep as possible along a branch before backtracking.

    How does it work?
    - Uses a 'stack' (LIFO: Last In, First Out).
    - Removes the most recently added state from the stack.
    - Generates all its neighbors (states 1 move away).
    - If a neighbor has never been visited, marks it as visited and adds it to the *top* of the stack.

    Returns:
        - path: A list of moves if a solution is found, or [] if not.
        - nodes_explored: How many states were analyzed.
        - max_depth: The maximum depth explored.
    """

    start_time = time.time()

    stack = [(initial_state, [])]

    # Set to track globally explored states to avoid revisiting.
    explored = set()

    # Counters for statistics.
    nodes_explored = 0
    max_depth = 0

    # Main loop: Continue while there are states to explore and time remains.
    while stack and time.time() - start_time < time_limit:
        # Remove the most recently added state/path from the stack (LIFO).
        state, path = stack.pop()
        nodes_explored += 1 

        # Generate a unique key for the current state.
        state_key = (tuple(map(tuple, state.board)), tuple(map(tuple, state.current_piece)))
        state_hash = hash(state_key)

        # Skip already explored states.
        if state_hash in explored:
            continue

        # Mark the state as explored.
        explored.add(state_hash)

        # Check if the goal state has been reached (all diamonds collected).
        if state.diamonds_collected >= state.total_diamonds:
            print(f"DFS: Diamond goal reached! Score: {state.score}")
            return path, nodes_explored, len(path)

        # Update the maximum depth reached.
        current_depth = len(path)
        max_depth = max(max_depth, current_depth)

        # Generate possible moves from the current state.
        possible_moves = state.get_possible_moves()

        if not possible_moves:
            continue

        # Iterate over the possible moves in reverse order to maintain DFS behavior.
        for move in reversed(possible_moves):
            next_state = state.apply_move(move)

            # Skip invalid or duplicate states.
            if next_state is None or next_state == state:
                continue

            # Add the new state and path to the stack.
            new_path = path + [move]
            stack.append((next_state, new_path))

    # If the loop ends (stack is empty or time limit is reached), no solution was found.
    print(f"DFS: Time limit reached or no solution found. Nodes: {nodes_explored}, Max Depth: {max_depth}")
    return [], nodes_explored, max_depth
