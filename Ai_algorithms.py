# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of AI options for Wood Block Puzzle Game

#--------------------------------------------

# Libraries:
import time
from game_state import GameState
from BFS import breadth_first_search
from DFS import depth_first_search
from UCS import uniform_cost_search
from DLS import depth_limited_search
from IDS import iterative_deepening_search
from GREEDY import greedy_search
from A_STAR import astar_search
from A_STAR_W import weighted_astar_search

#--------------------------------------------
# Gets best move from AI:

def get_ai_move(game, algorithm, time_limit=10, selected_heuristic=None):
    """
    Determines the optimal next move using the specified AI algorithm.
    """
    # Create a GameState object representing the current game state
    initial_state = GameState(game.board, game.current_piece, game.score)
    initial_state.diamonds_collected = game.diamonds_collected
    initial_state.total_diamonds = game.total_diamonds

    # Check if a heuristic is required for the selected algorithm
    if selected_heuristic is None and algorithm in ['greedy', 'astar', 'wastar']:
        print("Error: No heuristic provided for informed algorithms.")
        return None

    try:
        print(f"AI ({algorithm.upper()}) is thinking...")

        # Handle uninformed algorithms
        if algorithm == 'bfs':
            path, nodes_explored, max_depth = breadth_first_search(initial_state, time_limit)
            return path[0] if path else None
        elif algorithm == 'dfs':
            path, nodes_explored, max_depth = depth_first_search(initial_state, time_limit)
            return path[0] if path else None
        elif algorithm == 'ucs':
            path, nodes_explored, max_depth = uniform_cost_search(initial_state, time_limit)
            return path[0] if path else None
        elif algorithm == 'dls':
            depth_limit = 10  # Example depth limit
            path, nodes_explored, max_depth = depth_limited_search(initial_state, depth_limit, time_limit)
            return path[0] if path else None
        elif algorithm == 'ids':
            path, nodes_explored, max_depth = iterative_deepening_search(initial_state, time_limit)
            return path[0] if path else None

        # Handle informed algorithms
        elif algorithm in ['greedy', 'astar', 'wastar']:
            if not callable(selected_heuristic):
                print("Error: Invalid heuristic function provided.")
                return None

            # Generate possible moves and evaluate them using the heuristic
            possible_moves = initial_state.get_possible_moves()
            print(f"Possible moves: {possible_moves}")

            if not possible_moves:
                print("No valid moves found.")
                return None

            best_move = None
            best_score = float('inf')
            for move in possible_moves:
                x, y = move
                temp_state = GameState(initial_state.board, initial_state.current_piece, initial_state.score)
                if temp_state.place_piece(x, y):
                    g = temp_state.cost  # Cost to reach this state
                    h = selected_heuristic(temp_state)  # Heuristic value
                    if algorithm == 'greedy':
                        f = h  # Greedy only considers the heuristic
                    elif algorithm == 'astar':
                        f = g + h  # A* considers both cost and heuristic
                    elif algorithm == 'wastar':
                        weight = 1.5  # Example weight for Weighted A*
                        f = g + weight * h  # Weighted A* scales the heuristic

                    print(f"Move ({x}, {y}) -> g(n): {g}, h(n): {h}, f(n): {f}")

                    if f < best_score:
                        best_score = f
                        best_move = move

            print(f"Best move selected: {best_move}")
            return best_move

        else:
            print(f"Warning: Algorithm '{algorithm}' not recognized.")
            return None

    except Exception as e:
        print(f"!! Error during execution of algorithm {algorithm.upper()}: {e}")
        return None


#--------------------------------------------
# Heuristic: Diamond Proximity
def heuristic_diamond_proximity(state):
    """
    Heuristic to minimize the distance to the nearest diamond.
    Returns the minimum Manhattan distance from any valid piece placement to a diamond.
    """
    if not state.current_piece:
        print("No current piece available.")
        return float('inf')  # Return infinity if no piece is available

    min_distance = float('inf')
    piece = state.current_piece
    piece_height, piece_width = len(piece), len(piece[0])

    # Iterate through all possible placements of the piece
    for r in range(state.board_size - piece_height + 1):
        for c in range(state.board_size - piece_width + 1):
            valid_placement = True

            # Check if the piece can be placed at (r, c)
            for i in range(piece_height):
                for j in range(piece_width):
                    if piece[i][j] == 1:  # Part of the piece
                        if state.board[r + i][c + j] != " ":  # Check for collisions
                            valid_placement = False
                            break
                if not valid_placement:
                    break

            if valid_placement:
                # Calculate the Manhattan distance to the nearest diamond
                for board_r in range(state.board_size):
                    for board_c in range(state.board_size):
                        if state.board[board_r][board_c] == 'D':  # Found a diamond
                            for i in range(piece_height):
                                for j in range(piece_width):
                                    if piece[i][j] == 1:  # Part of the piece
                                        distance = abs(board_r - (r + i)) + abs(board_c - (c + j))
                                        min_distance = min(min_distance, distance)

    return min_distance if min_distance != float('inf') else 100  # Return a moderate value if no diamonds are present

#--------------------------------------------
# Heuristic: Maximize Score
def heuristic_maximize_score(state):
    """
    Heuristic to maximize the score.
    Evaluates potential moves and prioritizes those that increase the score the most.
    """
    max_score_gain = 0

    # Iterate through all possible placements of the current piece
    for r in range(state.board_size):
        for c in range(state.board_size):
            temp_state = GameState(state.board, state.current_piece, state.score)
            if temp_state.place_piece(r, c):
                temp_state._check_full_lines_and_columns()

                # Calculate the score gain
                score_gain = temp_state.score - state.score
                max_score_gain = max(max_score_gain, score_gain)

    # Return the negative of the max score gain (since lower heuristic values are better)
    return -max_score_gain

#--------------------------------------------

