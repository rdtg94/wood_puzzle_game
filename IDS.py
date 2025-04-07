# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of Iterative Deepening Search algorithm for the game.

#--------------------------------------------

"""
This file implements the Iterative Deepening Search (IDS) algorithm for solving a game problem.
IDS combines the advantages of BFS (finding the shortest path in terms of depth) and DFS
(lower memory usage). It performs multiple depth-limited searches, increasing the depth
limit with each iteration until a solution is found or the time limit is exceeded.

Returns:
    - path: The list of moves if a solution is found, or [] if not.
    - nodes_explored_overall: The total number of states analyzed across all iterations.
    - max_depth_overall: The maximum depth explored in any iteration.
"""

#-----------------------------------------------
# Libraries:

import time

#Importing the depth-limited search function from DLS module.
from DLS import depth_limited_search  
#-----------------------------------------------

def iterative_deepening_search(initial_state, time_limit):
    """
    This function performs Iterative Deepening Search (IDS).
    It combines the advantages of BFS and DFS by performing multiple depth-limited searches.

    How does it work?
    - Performs multiple Depth-Limited Searches (DLS), increasing the depth limit with each iteration.
    - Starts with a small depth limit (e.g., 1).
    - If no solution is found, increases the depth limit (e.g., to 2) and repeats the DLS.
    - Continues increasing the depth limit until a solution is found or the time limit is exceeded.
    - Guarantees finding the shallowest solution (like BFS) while using less memory (like DFS).

    Returns:
        - path: A list of moves if a solution is found, or [] if not.
        - nodes_explored_overall: The total number of states analyzed across all iterations.
        - max_depth_overall: The maximum depth explored in any iteration.
    """

    # Record the global start time for IDS.
    start_time = time.time()

    # Variables to accumulate overall statistics.
    max_depth_overall = 0
    nodes_explored_overall = 0
    found_path = []  # To store the solution path if found.

    # Main IDS loop: Increase the depth limit with each iteration.
    for depth_limit in range(1, 100):  # Arbitrary maximum depth limit (e.g., 100).
        # Check the elapsed time before starting a new DLS iteration.
        elapsed_time = time.time() - start_time
        if elapsed_time >= time_limit:
            print(f"IDS: Time limit reached ({elapsed_time:.2f}s) before starting DLS(depth={depth_limit}).")
            break

        # Calculate the remaining time for this specific DLS call.
        remaining_time = time_limit - elapsed_time
        if remaining_time <= 0:
            break

        print(f"IDS: Starting DLS with depth limit {depth_limit}, remaining time {remaining_time:.2f}s.")

        # Call the Depth-Limited Search (DLS) function with the current depth limit.
        path, nodes_in_iteration, max_depth_in_iteration = depth_limited_search(
            initial_state, remaining_time, depth_limit
        )

        # Accumulate the total nodes explored across all iterations.
        nodes_explored_overall += nodes_in_iteration
        # Update the maximum depth reached across all iterations.
        max_depth_overall = max(max_depth_overall, max_depth_in_iteration)

        # Check if the DLS found a solution (non-empty path).
        if path:
            print(f"IDS: Solution found at depth {depth_limit}.")
            found_path = path
            # Update the maximum depth if the solution path is deeper than previously recorded.
            max_depth_overall = max(max_depth_overall, len(path))
            break

        # Check the elapsed time after the DLS call.
        if time.time() - start_time >= time_limit:
            print(f"IDS: Time limit reached during or after DLS(depth={depth_limit}).")
            break

    # End of IDS loop.
    print(f"IDS: Finished. Total nodes explored: {nodes_explored_overall}, Max depth reached: {max_depth_overall}.")

    # Return the solution path (or empty if not found) and overall statistics.
    return found_path, nodes_explored_overall, max_depth_overall
