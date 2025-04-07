# Date: 2025-04-06
# Version: 1.1
# Author: Ricardo Gonçalves
# Description: Implementation of A* (A-Star) Search algorithm with heuristic selection.

#--------------------------------------------

"""
This file implements the A* (A-Star) Search algorithm for solving a game problem.
A* is a heuristic-based algorithm that balances the cost of reaching a state (g)
and an estimate of the cost to reach the goal (h). It guarantees finding the optimal
solution if the heuristic is admissible.

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
def astar_search(initial_state, time_limit, heuristic):
    """
    A* search algorithm.
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
                f = g + h
                heapq.heappush(frontier, (f, successor))

    print(f"Search terminated after exploring {nodes_explored} nodes.")
    return None, nodes_explored, 0
