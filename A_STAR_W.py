# Date: 2025-04-06
# Version: 1.1
# Author: Ricardo Gonçalves
# Description: Implementation of Weighted A* (Weighted A-Star) Search algorithm with heuristic selection.

#--------------------------------------------

"""
This file implements the Weighted A* (Weighted A-Star) Search algorithm for solving a game problem.
Weighted A* is a variation of A* that prioritizes the heuristic (h) by applying a weight to it.
This makes the algorithm faster but sacrifices optimality.

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
def weighted_astar_search(initial_state, time_limit, weight, heuristic):
    """
    Weighted A* search algorithm.
    """
    start_time = time.time()
    frontier = []
    heapq.heappush(frontier, (0, initial_state))  # Priority queue with (f(n), state)
    explored = set()
    nodes_explored = 0

    while frontier and time.time() - start_time < time_limit:
        f, current_state = heapq.heappop(frontier)
        nodes_explored += 1

        if current_state.is_goal_state():
            print(f"Goal state found after exploring {nodes_explored} nodes.")
            return current_state.get_path(), nodes_explored, current_state.depth

        explored.add(current_state)

        for successor in current_state.get_successors():
            if successor not in explored:
                g = successor.cost
                h = heuristic(successor)
                f = g + weight * h
                heapq.heappush(frontier, (f, successor))

    print(f"Search terminated after exploring {nodes_explored} nodes.")
    return None, nodes_explored, 0
