# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of BFS algorithm for the game.

#--------------------------------------------
"""
This file implements the Breadth-First Search (BFS) algorithm.
Finds the shortest path in terms of the number of moves.
"""
#-----------------------------------------------
#Libraries:
import time
from collections import deque
from game_state import GameState # Ensure GameState is importable

#------------------------------------------------
def breadth_first_search(initial_state: GameState, time_limit: float):
    """
    Performs Breadth-First Search (BFS).

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
    queue = deque([(initial_state, [])]) # Queue stores (state, path_to_state)
    explored = {hash(initial_state)} # Set stores hashes of explored states
    nodes_explored = 0
    max_depth = 0

    while queue:
        # Time limit check
        if time.time() - start_time >= time_limit:
            print(f"BFS: Time limit ({time_limit}s) reached.")
            return None, nodes_explored, max_depth

        current_state, path = queue.popleft()
        nodes_explored += 1
        current_depth = len(path)
        max_depth = max(max_depth, current_depth)

        # Goal check
        if current_state.is_goal_state():
            print(f"BFS: Goal state found! Score: {current_state.score}, Depth: {current_depth}")
            return path, nodes_explored, max_depth

        # Game over check (optional, but can prune branches)
        if current_state.is_game_over():
            continue

        # Explore successors
        for successor_state in current_state.get_successors():
            successor_hash = hash(successor_state)
            if successor_hash not in explored:
                explored.add(successor_hash)
                new_path = path + [successor_state.move] # Add the move that led to successor
                queue.append((successor_state, new_path))

    print(f"BFS: No solution found. Nodes explored: {nodes_explored}, Max depth: {max_depth}")
    return None, nodes_explored, max_depth
