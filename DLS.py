# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of Depth-Limited Search (DLS) algorithm for the game.

#--------------------------------------------

"""
This file implements the Depth-Limited Search (DLS) algorithm for solving a game problem.
It explores the state space using depth-first search but limits the depth of exploration
to avoid going too deep.
"""

#-----------------------------------------------
# Libraries:

import time

#-----------------------------------------------
def depth_limited_search(initial_state, time_limit, depth_limit=10):
    """
    This function performs Depth-Limited Search (DLS).
    It explores the state space using depth-first search with a depth limit.

    How does it work?
    - Uses recursion to explore the state space.
    - Stops exploring a branch if the depth limit is reached.
    - Returns 'cutoff' if the depth limit is reached without finding a solution.

    Returns:
        - path: A list of moves if a solution is found, or [] if not.
        - nodes_explored: How many states were analyzed.
        - max_depth_reached: The maximum depth explored.
    """

    start_time = time.time()

    # Counters for statistics.
    nodes_explored = 0
    max_depth_reached = 0

    # Recursive function for depth-limited search.
    def recursive_dls(state, path, depth):
        nonlocal nodes_explored, max_depth_reached, start_time

        # Increment the number of nodes explored.
        nodes_explored += 1

        # Update the maximum depth reached.
        max_depth_reached = max(max_depth_reached, depth)

        # Check if the time limit has been exceeded.
        if time.time() - start_time >= time_limit:
            return None, 'time_limit'

        # Check if the goal state has been reached (all diamonds collected).
        if state.diamonds_collected >= state.total_diamonds:
            print(f"DLS: Diamond goal reached! Score: {state.score}, Depth: {depth}")
            return path, 'found'

        # Check if the depth limit has been reached.
        if depth >= depth_limit:
            return None, 'cutoff'

        # Get all possible moves from the current state.
        possible_moves = state.get_possible_moves()
        if not possible_moves:
            return None, 'failure'

        # Explore each move.
        cutoff_occurred = False
        for move in possible_moves:
            next_state = state.apply_move(move)

            # Skip invalid or duplicate states.
            if next_state is None or next_state == state:
                continue

            # Recursively call DLS for the next state.
            new_path = path + [move]
            result_path, status = recursive_dls(next_state, new_path, depth + 1)

            if status == 'found':
                return result_path, 'found'
            if status == 'time_limit':
                return None, 'time_limit'
            if status == 'cutoff':
                cutoff_occurred = True

        # Return 'cutoff' if any branch was cut off, otherwise 'failure'.
        return None, 'cutoff' if cutoff_occurred else 'failure'

    # Start the recursive depth-limited search.
    result_path, status = recursive_dls(initial_state, [], 0)

    # Return the results based on the status.
    if status == 'found':
        return result_path, nodes_explored, max_depth_reached
    else:
        print(f"DLS: No solution found. Status: {status}, Nodes: {nodes_explored}, Max Depth: {max_depth_reached}")
        return [], nodes_explored, max_depth_reached
