# Date: 2025-04-07
# Version: 1.2
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of Weighted A* Search algorithm.

#--------------------------------------------
"""
This file implements the Weighted A* Search algorithm.
f(n) = g(n) + weight * h(n). Prioritizes heuristic more (if weight > 1).
Faster than A* but may sacrifice optimality.
"""
#-----------------------------------------------
# Libraries:
import time
import heapq
from game_state import GameState # Ensure GameState is importable
from constants import DEFAULT_WASTAR_WEIGHT

#-----------------------------------------------
def weighted_astar_search(initial_state: GameState, time_limit: float, weight: float, heuristic: callable):
    """
    Performs Weighted A* Search.

    Args:
        initial_state (GameState): The starting state.
        time_limit (float): Maximum execution time in seconds.
        weight (float): Weight applied to the heuristic (weight > 1 biases towards heuristic).
        heuristic (callable): Heuristic function `h(state)`.

    Returns:
        tuple: (path, nodes_explored, max_depth)
            - path (list | None): List of moves for a path if found, else None (not guaranteed optimal).
            - nodes_explored (int): Number of states explored.
            - max_depth (int): Maximum depth reached during search.
    """
    start_time = time.time()

    if not callable(heuristic):
        print("Weighted A* Error: Invalid heuristic function provided.")
        return None, 0, 0
    if weight < 0:
        print("Weighted A* Warning: Weight should generally be non-negative.")

    # Priority queue stores: (f_value, unique_id, state) where f = g + weight * h
    unique_id = 0
    g_initial = initial_state.cost
    h_initial = heuristic(initial_state)
    f_initial = g_initial + weight * h_initial
    frontier = [(f_initial, unique_id, initial_state)]
    heapq.heapify(frontier)
    unique_id += 1

    # explored stores {state_hash: min_g_cost_to_reach}
    # Important for Weighted A* as well to avoid redundant exploration,
    # although optimality isn't guaranteed, we still want efficiency.
    explored = {hash(initial_state): g_initial}

    nodes_explored = 0
    max_depth = 0

    while frontier:
        # Time limit check
        if time.time() - start_time >= time_limit:
            print(f"Weighted A*: Time limit ({time_limit}s) reached.")
            return None, nodes_explored, max_depth

        f_current, _, current_state = heapq.heappop(frontier)
        nodes_explored += 1
        max_depth = max(max_depth, current_state.depth)

        # Goal check
        if current_state.is_goal_state():
            print(f"Weighted A*: Goal state found! Score: {current_state.score}, Cost (g): {current_state.cost}, Depth: {current_state.depth}")
            return current_state.get_path(), nodes_explored, max_depth

        # Game over check (optional pruning)
        if current_state.is_game_over():
            continue

        # Optimization: If we found a shorter g-cost path to this state already, skip.
        current_hash = hash(current_state)
        if current_hash in explored and current_state.cost > explored[current_hash]:
             continue

        # Explore successors
        for successor_state in current_state.get_successors():
            successor_hash = hash(successor_state)
            g_successor = successor_state.cost

            # Check if successor is unexplored or found via a more expensive path (based on g-cost)
            if successor_hash not in explored or g_successor < explored[successor_hash]:
                explored[successor_hash] = g_successor # Update cost to reach successor
                h_successor = heuristic(successor_state)
                f_successor = g_successor + weight * h_successor
                heapq.heappush(frontier, (f_successor, unique_id, successor_state))
                unique_id += 1

    print(f"Weighted A*: No solution found. Nodes explored: {nodes_explored}, Max Depth: {max_depth}")
    return None, nodes_explored, max_depth
