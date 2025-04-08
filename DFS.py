# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of DFS algorithm for the game.

#--------------------------------------------
"""
This file implements the Depth-First Search (DFS) algorithm.
Explores as deeply as possible along each branch before backtracking.
"""
#-----------------------------------------------
# Libraries:
import time
from game_state import GameState # Ensure GameState is importable

#------------------------------------------------
def depth_first_search(initial_state: GameState, time_limit: float):
    """
    Performs Depth-First Search (DFS).

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum execution time in seconds.

    Returns:
        tuple: (path, nodes_explored, max_depth)
            - path (list | None): List of moves if solution found, else None.
            - nodes_explored (int): Number of states explored.
            - max_depth (int): Maximum depth reached.
    """
    start_time = time.time()
    stack = [(initial_state, [])] # Stack stores (state, path_to_state)
    # Explored set is crucial to prevent infinite loops in graphs with cycles
    # or redundant paths.
    explored = set()
    nodes_explored = 0
    max_depth = 0

    while stack:
        # Time limit check
        if time.time() - start_time >= time_limit:
            print(f"DFS: Time limit ({time_limit}s) reached.")
            return None, nodes_explored, max_depth

        current_state, path = stack.pop()
        nodes_explored += 1
        current_depth = len(path)
        max_depth = max(max_depth, current_depth)

        current_hash = hash(current_state)
        # Check if already explored *after* popping, common DFS optimization
        if current_hash in explored:
            continue
        explored.add(current_hash)

        # Goal check
        if current_state.is_goal_state():
            print(f"DFS: Goal state found! Score: {current_state.score}, Depth: {current_depth}")
            return path, nodes_explored, max_depth

        # Game over check (optional pruning)
        if current_state.is_game_over():
            continue

        # Explore successors - Add successors to the stack
        # Reversing helps explore paths in a more 'natural' order sometimes, but not strictly necessary
        successors = current_state.get_successors()
        # for successor_state in reversed(successors): # Optional reverse
        for successor_state in successors:
            # Check explored *before* pushing to potentially save stack space,
            # but checking after popping (as done above) is also valid for correctness.
            # successor_hash = hash(successor_state)
            # if successor_hash not in explored:
            new_path = path + [successor_state.move]
            stack.append((successor_state, new_path))


    print(f"DFS: No solution found. Nodes explored: {nodes_explored}, Max Depth: {max_depth}")
    return None, nodes_explored, max_depth
