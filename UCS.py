# Date: 2021-09-26
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of UCS algorithm for the game.


#--------------------------------------------

"""
This file implements the Uniform Cost Search (UCS) algorithm for solving a game problem.
It explores the state space to find the path with the lowest cumulative cost (g(n)).
The implementation uses a priority queue for state management and tracks explored states
to avoid revisiting them. The algorithm guarantees finding the optimal solution if all
step costs are non-negative.

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
def uniform_cost_search(initial_state, time_limit):
    """
    This function performs Uniform Cost Search (UCS).
    It finds the path with the lowest cumulative cost (g(n)).

    How does it work?
    - Uses a 'priority queue' to expand the state with the lowest cost first.
    - The cost is defined as the cumulative cost (g(n)) to reach a state.
    - Guarantees finding the optimal solution if all step costs are non-negative.

    Returns:
        - path: A list of moves if a solution is found, or [] if not.
        - nodes_explored: How many states were analyzed.
        - max_depth: The maximum depth explored.
    """

    start_time = time.time()

    # Priority queue: (cumulative_cost, tie_breaker, state, path)
    priority_queue = [(0, 0, initial_state, [])]

    # Dictionary to track the minimum cost to reach each state.
    # Key: hash of the state, Value: cumulative cost.
    initial_key = (tuple(map(tuple, initial_state.board)), tuple(map(tuple, initial_state.current_piece)))
    explored = {hash(initial_key): 0}

    # Counters for statistics.
    nodes_explored = 0
    max_depth = 0
    counter = 1  # Tie-breaker counter for priority queue.

    while priority_queue and time.time() - start_time < time_limit:
        # Remove the state with the lowest cumulative cost (g(n)) from the queue.
        current_cost, _, state, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        # Check if the goal state has been reached (all diamonds collected).
        if state.diamonds_collected >= state.total_diamonds:
            print(f"UCS: Diamond goal reached! Score: {state.score}, Cost (moves): {current_cost}")
            return path, nodes_explored, len(path)

        # Update the maximum depth reached.
        current_depth = len(path)
        max_depth = max(max_depth, current_depth)

        # Generate possible moves from the current state.
        possible_moves = state.get_possible_moves()
        if not possible_moves:
            continue

        for move in possible_moves:
            # Apply the move to generate the next state.
            next_state = state.apply_move(move)

            # Skip invalid or duplicate states.
            if next_state is None or next_state == state:
                continue

            # Define the cost of this move.
            move_cost = 1  # Each move has a cost of 1.
            new_cost = current_cost + move_cost  # Calculate the cumulative cost.
            new_path = path + [move]  # Update the path.

            # Generate a unique key for the next state.
            next_key = (tuple(map(tuple, next_state.board)), tuple(map(tuple, next_state.current_piece)))
            next_hash = hash(next_key)

            # Check if this new path to 'next_state' has a lower cost than previously recorded.
            if new_cost < explored.get(next_hash, float('inf')):
                # Update the minimum cost for this state.
                explored[next_hash] = new_cost
                # Add the state, its new cost, and path to the priority queue.
                heapq.heappush(priority_queue, (new_cost, counter, next_state, new_path))
                counter += 1  # Increment the tie-breaker counter.

    # If the loop ends (queue is empty or time limit is reached), no solution was found.
    print(f"UCS: Time limit reached or no solution found. Nodes: {nodes_explored}, Max Depth: {max_depth}")
    return [], nodes_explored, max_depth
