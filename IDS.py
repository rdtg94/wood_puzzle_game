# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of Iterative Deepening Search algorithm.

#--------------------------------------------
"""
This file implements the Iterative Deepening Search (IDS) algorithm.
Combines benefits of BFS (completeness, optimality for unit costs) and DFS (memory).
"""
#-----------------------------------------------
# Libraries:
import time
from game_state import GameState # Ensure GameState is importable
from DLS import depth_limited_search # Import DLS function
from constants import DEFAULT_IDS_MAX_DEPTH

#-----------------------------------------------

def iterative_deepening_search(initial_state: GameState, time_limit: float):
    """
    Performs Iterative Deepening Search (IDS).

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum total execution time in seconds.

    Returns:
        tuple: (path, nodes_explored_total, max_depth_total)
            - path (list | None): List of moves if solution found, else None.
            - nodes_explored_total (int): Total nodes explored across all DLS iterations.
            - max_depth_total (int): Maximum depth reached in the final successful iteration or overall.
    """
    start_time = time.time()
    nodes_explored_total = 0
    max_depth_total = 0
    solution_path = None

    # Iterate through increasing depth limits
    for depth_limit in range(DEFAULT_IDS_MAX_DEPTH): # Iterate up to a max depth
        elapsed_time = time.time() - start_time
        remaining_time = time_limit - elapsed_time

        if remaining_time <= 0:
            print(f"IDS: Time limit ({time_limit}s) reached before starting depth {depth_limit}.")
            break

        # print(f"IDS: Starting DLS with depth limit {depth_limit}, Remaining time: {remaining_time:.2f}s")

        # Perform DLS for the current depth limit
        path, nodes_in_iter, depth_in_iter = depth_limited_search(
            initial_state, remaining_time, depth_limit
        )

        # Accumulate statistics
        nodes_explored_total += nodes_in_iter
        max_depth_total = max(max_depth_total, depth_in_iter) # Track max depth reached overall

        # Check if DLS returned due to time limit within DLS itself
        current_elapsed = time.time() - start_time
        if current_elapsed >= time_limit and not path: # Check if time ran out AND no solution found this iter
             print(f"IDS: Time limit ({time_limit}s) likely reached during DLS(depth={depth_limit}).")
             break # Stop IDS

        # Check if DLS found a solution
        if path is not None:
            print(f"IDS: Solution found at depth {depth_limit}!")
            solution_path = path
            # Update max_depth_total specifically to the solution depth if found
            max_depth_total = max(max_depth_total, len(path))
            break # Solution found, exit IDS loop

        # If DLS returned None and status wasn't 'cutoff' (implicitly checked by path is None),
        # it means the search space was exhausted up to this depth without finding a solution or hitting the limit.
        # If DLS returned None because of 'cutoff', IDS continues to the next depth.

    # End of IDS loop
    if solution_path:
        print(f"IDS: Finished. Solution found. Total nodes: {nodes_explored_total}, Solution Depth: {len(solution_path)}")
    else:
        print(f"IDS: Finished. No solution found (or time limit reached). Total nodes: {nodes_explored_total}, Max depth explored: {max_depth_total}")

    return solution_path, nodes_explored_total, max_depth_total
