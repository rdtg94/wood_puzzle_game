# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of Depth-Limited Search (DLS) algorithm.

#--------------------------------------------
"""
This file implements the Depth-Limited Search (DLS) algorithm.
Performs DFS up to a specified depth limit.
"""
#-----------------------------------------------
# Libraries:
import time
from game_state import GameState # Ensure GameState is importable
from constants import DEFAULT_DLS_DEPTH_LIMIT

#-----------------------------------------------
# Global or shared counters for DLS within IDS context if needed,
# otherwise, they are local to each DLS call.
# For standalone DLS, these are reset each time.
nodes_explored_dls = 0
max_depth_reached_dls = 0
time_limit_reached_flag = False

def depth_limited_search(initial_state: GameState, time_limit: float, depth_limit: int = DEFAULT_DLS_DEPTH_LIMIT):
    """
    Performs Depth-Limited Search (DLS).

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum execution time in seconds.
        depth_limit (int): The maximum depth to explore.

    Returns:
        tuple: (path, nodes_explored, max_depth_reached)
            - path (list | None): List of moves if solution found within limit, else None.
            - nodes_explored (int): Number of states explored in this DLS run.
            - max_depth_reached (int): Maximum depth reached in this DLS run.
    """
    global nodes_explored_dls, max_depth_reached_dls, time_limit_reached_flag
    # Reset counters for this specific DLS call
    nodes_explored_dls = 0
    max_depth_reached_dls = 0
    time_limit_reached_flag = False
    start_time = time.time()
    explored_in_path = set() # Track nodes in the current recursion path to avoid cycles

    result_path, status = recursive_dls(initial_state, [], 0, depth_limit, time_limit, start_time, explored_in_path)

    if time_limit_reached_flag:
        print(f"DLS: Time limit ({time_limit}s) reached during search.")
        return None, nodes_explored_dls, max_depth_reached_dls

    if status == 'found':
        return result_path, nodes_explored_dls, max_depth_reached_dls
    elif status == 'cutoff':
        # print(f"DLS: Cutoff occurred at depth {depth_limit}.")
        pass # Normal in IDS context
    elif status == 'failure':
        # print(f"DLS: Failure - no solution found within depth limit.")
        pass

    return None, nodes_explored_dls, max_depth_reached_dls


def recursive_dls(state: GameState, path: list, depth: int, limit: int, time_limit: float, start_time: float, explored_path: set):
    """Recursive helper function for DLS."""
    global nodes_explored_dls, max_depth_reached_dls, time_limit_reached_flag

    # Time limit check
    if time.time() - start_time >= time_limit:
        time_limit_reached_flag = True
        return None, 'time_limit'

    nodes_explored_dls += 1
    max_depth_reached_dls = max(max_depth_reached_dls, depth)

    # Goal check
    if state.is_goal_state():
        print(f"DLS: Goal state found! Score: {state.score}, Depth: {depth}")
        return path, 'found'

    # Depth limit check
    if depth >= limit:
        return None, 'cutoff'

    # Game over check (optional pruning)
    if state.is_game_over():
        return None, 'failure' # Treat game over as failure branch

    # Cycle detection for the current path
    state_hash = hash(state)
    if state_hash in explored_path:
        return None, 'failure' # Cycle detected in current path
    explored_path.add(state_hash)


    cutoff_occurred = False
    successors = state.get_successors()

    if not successors:
         explored_path.remove(state_hash) # Backtrack
         return None, 'failure' # No successors from this state

    for successor_state in successors:
        new_path = path + [successor_state.move]
        result_path, status = recursive_dls(successor_state, new_path, depth + 1, limit, time_limit, start_time, explored_path)

        if status == 'found':
            explored_path.remove(state_hash) # Backtrack
            return result_path, 'found'
        if status == 'time_limit':
            explored_path.remove(state_hash) # Backtrack
            return None, 'time_limit'
        if status == 'cutoff':
            cutoff_occurred = True
        # Continue if status is 'failure'

    explored_path.remove(state_hash) # Backtrack: remove state from current path exploration
    return None, 'cutoff' if cutoff_occurred else 'failure'
