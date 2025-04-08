# Date: 2025-04-07
# Version: 1.2
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of Greedy Best-First Search algorithm.

#--------------------------------------------
"""
This file implements the Greedy Best-First Search algorithm.
Prioritizes states based solely on the heuristic value (h(n)). Fast but not optimal.
"""
#-----------------------------------------------
# Libraries:
import time
import heapq
from game_state import GameState # Ensure GameState is importable

#-----------------------------------------------
def greedy_search(initial_state: GameState, time_limit: float, heuristic: callable):
    """
    Performs Greedy Best-First Search.

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum execution time in seconds.
        heuristic (callable): Function `h(state)` estimating cost to goal.

    Returns:
        tuple: (path, nodes_explored, max_depth)
            - path (list | None): List of moves if solution found, else None.
            - nodes_explored (int): Number of states explored.
            - max_depth (int): Maximum depth reached.
    """
    start_time = time.time()

    if not callable(heuristic):
        print("GREEDY Error: Invalid heuristic function provided.")
        return None, 0, 0

    # Priority queue stores: (heuristic_value, unique_id, state)
    unique_id = 0
    h_initial = heuristic(initial_state)
    frontier = [(h_initial, unique_id, initial_state)]
    heapq.heapify(frontier)
    unique_id += 1

    # explored stores hashes of visited states to avoid cycles/redundancy
    explored = {hash(initial_state)}

    nodes_explored = 0
    max_depth = 0

    while frontier:
        # Time limit check
        if time.time() - start_time >= time_limit:
            print(f"GREEDY: Time limit ({time_limit}s) reached.")
            return None, nodes_explored, max_depth

        _, _, current_state = heapq.heappop(frontier)
        nodes_explored += 1
        max_depth = max(max_depth, current_state.depth)

        # Goal check
        if current_state.is_goal_state():
            print(f"GREEDY: Goal state found! Score: {current_state.score}, Depth: {current_state.depth}")
            return current_state.get_path(), nodes_explored, max_depth

        # Game over check (optional pruning)
        if current_state.is_game_over():
            continue

        # Explore successors
        for successor_state in current_state.get_successors():
            successor_hash = hash(successor_state)
            if successor_hash not in explored:
                explored.add(successor_hash)
                h_successor = heuristic(successor_state)
                heapq.heappush(frontier, (h_successor, unique_id, successor_state))
                unique_id += 1

    print(f"GREEDY: No solution found. Nodes explored: {nodes_explored}, Max Depth: {max_depth}")
    return None, nodes_explored, max_depth
