# Date: 2025-04-06
# Version: 1.1
# Author: Ricardo Gonçalves
# Description: Implementation of Greedy Search algorithm with heuristic selection.

#--------------------------------------------

"""
This file implements the Greedy Best-First Search (Greedy Search) algorithm for solving a game problem.
Greedy Search is a heuristic-based algorithm that prioritizes states that appear closest to the goal
based on a heuristic function. It is fast but does not guarantee finding the optimal solution.

Returns:
    - path: The list of moves if a solution is found, or [] if not.
    - nodes_explored: The number of states analyzed.
    - max_depth: The maximum depth explored within the given time limit.
"""

#-----------------------------------------------
# Libraries:

import time
import heapq

#-----------------------------------------------
def greedy_search(initial_state, time_limit, heuristic):
    """
    Performs Greedy Best-First Search (Greedy Search).
    It prioritizes states that appear closest to the goal based on a heuristic function.

    Args:
        initial_state (GameState): The initial state of the game.
        time_limit (int): The maximum time allowed for the search (in seconds).
        heuristic (function): The heuristic function to use for estimating the cost to the goal.

    Returns:
        tuple: (path, nodes_explored, max_depth)
            - path: A list of moves leading to the goal state, or None if no solution is found.
            - nodes_explored: The number of states explored during the search.
            - max_depth: The maximum depth reached during the search.
    """
    start_time = time.time()
    frontier = []  # Priority queue for states
    heapq.heappush(frontier, (heuristic(initial_state), initial_state))  # Push initial state with its heuristic value
    explored = set()  # Set to track explored states
    nodes_explored = 0
    max_depth = 0

    while frontier and time.time() - start_time < time_limit:
        # Pop the state with the lowest heuristic value
        _, current_state = heapq.heappop(frontier)
        nodes_explored += 1
        max_depth = max(max_depth, current_state.depth)

        # Check if the current state is a goal state
        if current_state.is_goal_state():
            return current_state.get_path(), nodes_explored, max_depth

        # Add the current state to the explored set
        explored.add(current_state)

        # Generate successors
        for successor in current_state.get_successors():
            if successor not in explored:
                heapq.heappush(frontier, (heuristic(successor), successor))

    # If no solution is found within the time limit
    return None, nodes_explored, max_depth
