# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of UCS algorithm for the game.

#--------------------------------------------
"""
This file implements the Uniform Cost Search (UCS) algorithm.
Finds the path with the lowest cumulative cost (g(n)).
"""
#-----------------------------------------------
# Libraries:
import time
import heapq
from game_state import GameState # Ensure GameState is importable

#-----------------------------------------------
def uniform_cost_search(initial_state: GameState, time_limit: float):
    """
    Performs Uniform Cost Search (UCS).

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum execution time in seconds.

    Returns:
        tuple: (path, nodes_explored, max_depth)
            - path (list | None): List of moves if solution found, else None.
            - nodes_explored (int): Number of states explored.
            - max_depth (int): Maximum depth reached during search.
    """
    start_time = time.time()
    # Priority queue stores: (cost, unique_id, state)
    # unique_id is a tie-breaker to handle states with the same cost.
    unique_id = 0
    frontier = [(initial_state.cost, unique_id, initial_state)]
    heapq.heapify(frontier)
    unique_id += 1

    # explored stores {state_hash: min_cost_to_reach}
    explored = {hash(initial_state): initial_state.cost}

    nodes_explored = 0
    max_depth = 0

    while frontier:
        # Time limit check
        if time.time() - start_time >= time_limit:
            print(f"UCS: Time limit ({time_limit}s) reached.")
            return None, nodes_explored, max_depth

        current_cost, _, current_state = heapq.heappop(frontier)
        nodes_explored += 1
        max_depth = max(max_depth, current_state.depth)

        # Goal check
        if current_state.is_goal_state():
            print(f"UCS: Goal state found! Score: {current_state.score}, Cost: {current_cost}, Depth: {current_state.depth}")
            return current_state.get_path(), nodes_explored, max_depth

        # Game over check (optional pruning)
        if current_state.is_game_over():
            continue

        # If we found a shorter path to this state already, skip
        # This check is implicitly handled by the explored check below,
        # but can be explicit: if current_cost > explored[hash(current_state)]: continue

        # Explore successors
        for successor_state in current_state.get_successors():
            successor_hash = hash(successor_state)
            new_cost = successor_state.cost # Cost is updated in apply_move/GameState init

            # Check if successor is unexplored or found with a higher cost
            if successor_hash not in explored or new_cost < explored[successor_hash]:
                explored[successor_hash] = new_cost
                heapq.heappush(frontier, (new_cost, unique_id, successor_state))
                unique_id += 1

    print(f"UCS: No solution found. Nodes explored: {nodes_explored}, Max Depth: {max_depth}")
    return None, nodes_explored, max_depth
