# Date: 2025-04-07
# Version: 1.2
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of AI options for Wood Block Puzzle Game

#--------------------------------------------

# Libraries:
import time
from game_state import GameState
from constants import DEFAULT_AI_TIME_LIMIT, DEFAULT_DLS_DEPTH_LIMIT, DEFAULT_WASTAR_WEIGHT

# Import search algorithm functions
from BFS import breadth_first_search
from DFS import depth_first_search
from UCS import uniform_cost_search
from DLS import depth_limited_search
from IDS import iterative_deepening_search
from GREEDY import greedy_search
from A_STAR import astar_search
from A_STAR_W import weighted_astar_search

# Import heuristics
#--------------------------------------------
# Heuristic: Diamond Proximity (Optimized)
def heuristic_diamond_proximity(state):
    """
    Heuristic: Minimize distance to the nearest diamond.
    Optimized: Finds diamonds once, then checks distance from valid placements.
    """
    if not state.current_piece:
        return float('inf')

    # 1. Find all diamond locations once
    diamond_locations = []
    for r in range(state.board_size):
        for c in range(state.board_size):
            if state.board[r][c] == 'D':
                diamond_locations.append((r, c))

    # If no diamonds, return a high value (less desirable state)
    if not diamond_locations:
        from constants import HEURISTIC_DIAMOND_PROXIMITY_NO_DIAMOND_VALUE
        return HEURISTIC_DIAMOND_PROXIMITY_NO_DIAMOND_VALUE # Or 0 if proximity isn't relevant

    min_dist_to_diamond = float('inf')
    possible_moves = state.get_possible_moves()

    if not possible_moves:
        return float('inf') # No moves possible

    # 2. Iterate through valid placements only
    for r_place, c_place in possible_moves:
        piece_height, piece_width = len(state.current_piece), len(state.current_piece[0])
        placement_min_dist = float('inf')

        # 3. For each placement, find the minimum distance from any piece cell to any diamond
        for i in range(piece_height):
            for j in range(piece_width):
                if state.current_piece[i][j] == 1: # If this is part of the piece
                    piece_cell_r, piece_cell_c = r_place + i, c_place + j
                    # Find distance to nearest diamond from this piece cell
                    for diamond_r, diamond_c in diamond_locations:
                        distance = abs(piece_cell_r - diamond_r) + abs(piece_cell_c - diamond_c)
                        placement_min_dist = min(placement_min_dist, distance)

        # Update the overall minimum distance found across all placements
        min_dist_to_diamond = min(min_dist_to_diamond, placement_min_dist)

    # Return the smallest distance found (lower is better)
    # If still infinity (e.g., piece covers only non-diamond cells), return default high value
    return min_dist_to_diamond if min_dist_to_diamond != float('inf') else HEURISTIC_DIAMOND_PROXIMITY_NO_DIAMOND_VALUE

#--------------------------------------------
# Heuristic: Maximize Score (Lookahead Version)
def heuristic_maximize_score(state):
     """
     Heuristic: Estimates score gain from the *next* move.
     Evaluates potential moves and prioritizes those that seem to increase the score the most immediately.
     Returns the negative of the max score gain (lower heuristic values are better for minimization algorithms).
     """
     max_score_gain = -float('inf') # Use -inf to correctly find the maximum gain (even if it's negative)

     possible_moves = state.get_possible_moves()
     if not possible_moves:
         # No moves possible from this state, implies zero potential gain from here.
         # Returning 0 is neutral. Returning a large positive value would make the state undesirable.
         return 0

     initial_score = state.score

     for move in possible_moves:
         # Simulate applying the move to get the resulting state
         # apply_move handles placing, clearing lines/cols, and score update internally
         temp_state = state.apply_move(move)
         if temp_state:
             # Calculate the score change resulting from this single move
             score_gain = temp_state.score - initial_score
             # Keep track of the best score gain found so far
             max_score_gain = max(max_score_gain, score_gain)
         else:
             # If apply_move returns None (shouldn't happen for valid moves), treat as 0 gain
             max_score_gain = max(max_score_gain, 0)


     # If max_score_gain is still -inf (e.g., all moves failed simulation, very unlikely), return 0
     if max_score_gain == -float('inf'):
         return 0

     # Return the negative of the maximum potential score gain.
     # Why negative? Search algorithms (like A*, Greedy) aim to *minimize* the heuristic value.
     # A higher score gain is better, so we make its corresponding heuristic value lower (more negative).
     return -max_score_gain

#--------------------------------------------
# Heuristic: First Available Move (for Instant Hint)
def heuristic_first_move(state):
    """
    Finds the first valid move possible.
    Not a real heuristic for search, but provides an instant suggestion.
    Returns the move (r, c) or None.
    NOTE: This logic is typically called directly by the GUI hint function,
          not used within standard search algorithms like A*.
          It returns a *move*, not a heuristic *value*.
    """
    if not state.current_piece:
        return None

    piece_height, piece_width = len(state.current_piece), len(state.current_piece[0])
    for r in range(state.board_size - piece_height + 1):
        for c in range(state.board_size - piece_width + 1):
            # Check if the piece can be placed at (r, c)
            valid_placement = True
            for i in range(piece_height):
                for j in range(piece_width):
                    if state.current_piece[i][j] == 1:  # Part of the piece
                        if state.board[r + i][c + j] != " ":  # Check for collisions
                            valid_placement = False
                            break
                if not valid_placement:
                    break
            # If it's a valid placement, return this move immediately
            if valid_placement:
                return (r, c)

    # No valid move found
    return None

#--------------------------------------------
# Gets best move from AI:

def get_ai_move(game, algorithm, time_limit=DEFAULT_AI_TIME_LIMIT, selected_heuristic=None):
    """
    Determines the optimal *first* move using the specified AI algorithm.
    Calls the appropriate search function and returns the first step of the path.
    """
    # Create a GameState object representing the current live game state
    # Support both GUI and shell game objects which may use different
    # attribute names for the current piece
    current_piece = getattr(game, 'current_piece', None)
    if current_piece is None:
        current_piece = getattr(game, 'current_piece_shape', None)

    initial_state = GameState(
        board=game.board,
        current_piece=current_piece,
        score=game.score,
        difficulty=game.difficulty,
        diamonds_collected=game.diamonds_collected,
        total_diamonds=game.total_diamonds
        # cost, parent, move are implicitly 0/None for the root state
    )

    # Check if a heuristic is required and provided for informed algorithms
    is_informed = algorithm in ['greedy', 'astar', 'wastar']
    if is_informed and not callable(selected_heuristic):
        print(f"Error: Heuristic function required for {algorithm.upper()} but not provided or invalid.")
        return None

    start_time = time.time()
    path = None
    nodes_explored = 0
    max_depth = 0
    best_move = None

    try:
        print(f"\nAI ({algorithm.upper()}) thinking... (Time Limit: {time_limit}s)")
        if selected_heuristic:
            print(f"Using Heuristic: {selected_heuristic.__name__}")

        # --- Call the Correct Search Algorithm ---
        if algorithm == 'bfs':
            path, nodes_explored, max_depth = breadth_first_search(initial_state, time_limit)
        elif algorithm == 'dfs':
            path, nodes_explored, max_depth = depth_first_search(initial_state, time_limit)
        elif algorithm == 'ucs':
            path, nodes_explored, max_depth = uniform_cost_search(initial_state, time_limit)
        elif algorithm == 'dls':
            depth_limit = DEFAULT_DLS_DEPTH_LIMIT # Use constant
            path, nodes_explored, max_depth = depth_limited_search(initial_state, time_limit, depth_limit)
        elif algorithm == 'ids':
            path, nodes_explored, max_depth = iterative_deepening_search(initial_state, time_limit)
        elif algorithm == 'greedy':
            path, nodes_explored, max_depth = greedy_search(initial_state, time_limit, selected_heuristic)
        elif algorithm == 'astar':
            path, nodes_explored, max_depth = astar_search(initial_state, time_limit, selected_heuristic)
        elif algorithm == 'wastar':
            weight = DEFAULT_WASTAR_WEIGHT # Use constant
            path, nodes_explored, max_depth = weighted_astar_search(initial_state, time_limit, weight, selected_heuristic)
        else:
            print(f"Warning: Algorithm '{algorithm}' not recognized.")
            return None

        # --- Process Results ---
        elapsed_time = time.time() - start_time
        print(f"AI ({algorithm.upper()}) finished in {elapsed_time:.2f}s.")
        print(f"Nodes Explored: {nodes_explored}, Max Depth Reached: {max_depth}")

        if path:
            if isinstance(path, list) and len(path) > 0:
                best_move = path[0] # Get the first move from the path
                print(f"Best move suggested: {best_move}")
            else:
                # This case might happen if the goal is reached at the initial state (path=[])
                # Or if the algorithm returns something unexpected.
                if isinstance(path, list) and len(path) == 0:
                     print("AI determined goal state is already reached or no moves needed/possible.")
                else:
                     print(f"Warning: Algorithm returned an unexpected path format: {path}")
                best_move = None
        else:
            print("AI could not find a solution path.")
            best_move = None

        return best_move

    except Exception as e:
        print(f"!! Error during execution of algorithm {algorithm.upper()}: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
        return None

#--------------------------------------------
