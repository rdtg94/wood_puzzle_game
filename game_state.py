# Date: 2025-04-07
# Version: 1.1
# Author: Ricardo Gonçalves (rdtg94)
# Description: Implementation of GameState Class for Wood Block Puzzle Game AI.

#--------------------------------------------

#Libraries:
import copy
import random
from constants import (
    SCORE_PENALTY_PLACE_PIECE, SCORE_BASE_LINE_CLEAR, SCORE_DIAMOND_BONUS,
    SCORE_COMBO_BONUS_DIVISOR, DEFAULT_MOVE_COST,
    DIFFICULTY_MEDIUM_PIECES, DIFFICULTY_HARD_PIECES, DIFFICULTY_EXPERT_PIECES
)

#--------------------------------------------
#Classes:

class GameState:
    """
    Represents a state (a snapshot) of the game to be used by AI algorithms.
    Manages board, piece, score, cost, depth, and transitions for search.
    """
#--------------------------------------------
#Constructs a GameState object:

    def __init__(self, board, current_piece, score, difficulty=1, cost=0, parent=None, move=None, diamonds_collected=0, total_diamonds=0):
        """
        Initializes a GameState object.

        Args:
            board (list): The current state of the game board.
            current_piece (list): The current piece to be placed.
            score (int): The current score of the game.
            difficulty (int): The difficulty level (1-4).
            cost (int): The cumulative cost to reach this state (default is 0).
            parent (GameState): The parent state (default is None).
            move (tuple): The move (e.g., (x, y)) that led to this state.
            diamonds_collected (int): Diamonds collected so far to reach this state.
            total_diamonds (int): Total diamonds initially on the board.
        """
        # Deep copy to ensure independence
        self.board = copy.deepcopy(board)
        self.current_piece = copy.deepcopy(current_piece)
        self.score = score
        self.difficulty = difficulty
        self.cost = cost
        self.parent = parent
        self.move = move
        self.depth = parent.depth + 1 if parent else 0
        self.board_size = len(board)

        # State-specific counters (inherited or calculated)
        self.diamonds_collected = diamonds_collected
        # Calculate total diamonds if not provided (e.g., for initial state)
        self.total_diamonds = total_diamonds if total_diamonds > 0 else sum(row.count("D") for row in board)

#--------------------------------------------
# Static method for piece generation (used by GameState and WoodBlockPuzzle)

    @staticmethod
    def _generate_random_piece(difficulty):
        """Generate a random piece based on difficulty level."""
        basic_shapes = [
            [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1], [1], [1]]
        ]
        medium_shapes = [
            [[1, 1], [1, 1]], [[1, 1], [1, 0]], [[1, 1], [0, 1]], [[1, 0], [1, 1]]
        ]
        hard_shapes = [
            [[1, 1, 1], [1, 0, 0]], [[1, 1, 1], [0, 0, 1]], [[1, 0], [1, 0], [1, 1]]
        ]
        expert_shapes = [
            [[1, 1, 1], [0, 1, 0]], [[0, 1, 0], [1, 1, 1]], [[1, 1, 0], [0, 1, 1]]
        ]

        available_shapes = basic_shapes[:]
        if difficulty >= DIFFICULTY_MEDIUM_PIECES:
            available_shapes.extend(medium_shapes)
        if difficulty >= DIFFICULTY_HARD_PIECES:
            available_shapes.extend(hard_shapes)
        if difficulty >= DIFFICULTY_EXPERT_PIECES:
            available_shapes.extend(expert_shapes)

        return random.choice(available_shapes) if available_shapes else [[1]] # Fallback

#--------------------------------------------
# Check if piece can be placed:

    def _can_place_piece(self, r, c):
        """Checks if the current piece can be placed at position (r, c)."""
        if not self.current_piece:
            return False

        piece_height, piece_width = len(self.current_piece), len(self.current_piece[0])

        # Boundary check
        if r < 0 or c < 0 or r + piece_height > self.board_size or c + piece_width > self.board_size:
            return False

        # Collision check
        for i in range(piece_height):
            for j in range(piece_width):
                if self.current_piece[i][j] == 1:
                    if self.board[r + i][c + j] != " ": # Check against obstacles, diamonds, or placed pieces
                        return False
        return True

#--------------------------------------------
# Get all valid moves:

    def get_possible_moves(self):
        """Returns a list of valid (r, c) coordinates where the current piece can be placed."""
        moves = []
        if not self.current_piece:
            return moves
        piece_height, piece_width = len(self.current_piece), len(self.current_piece[0])
        for r in range(self.board_size - piece_height + 1):
            for c in range(self.board_size - piece_width + 1):
                if self._can_place_piece(r, c):
                    moves.append((r, c))
        return moves

#--------------------------------------------
# Internal method to place piece on THIS state's board (used by apply_move)

    def _place_piece_on_board(self, r, c):
        """Places the current piece at (r, c) on this state's board. Assumes _can_place_piece was checked."""
        if not self.current_piece: return False
        piece_height, piece_width = len(self.current_piece), len(self.current_piece[0])
        for i in range(piece_height):
            for j in range(piece_width):
                if self.current_piece[i][j] == 1:
                    self.board[r + i][c + j] = "#"
        # Apply placement penalty
        self.score -= SCORE_PENALTY_PLACE_PIECE # Simple penalty for placing
        return True

#--------------------------------------------
# Internal method to check and clear lines/columns on THIS state's board

    def _check_and_clear_lines_columns(self):
        """
        Checks for full lines/columns on THIS state's board, clears them,
        updates score, and counts collected diamonds.
        NOTE: This logic is duplicated in WoodBlockPuzzle for the live game.
              Keep them synchronized if rules change.
        """
        lines_to_clear = []
        columns_to_clear = []
        diamonds_captured_this_clear = 0

        # Check full lines
        for r in range(self.board_size):
            if all(self.board[r][c] in ["#", "D"] for c in range(self.board_size)):
                lines_to_clear.append(r)

        # Check full columns
        for c in range(self.board_size):
            if all(self.board[r][c] in ["#", "D"] for r in range(self.board_size)):
                columns_to_clear.append(c)

        if not lines_to_clear and not columns_to_clear:
            return 0 # Return number of diamonds captured

        cleared_cells = set()

        # Clear lines and count diamonds
        for r in lines_to_clear:
            for c in range(self.board_size):
                cell_coord = (r, c)
                if cell_coord not in cleared_cells:
                    if self.board[r][c] == "D":
                        diamonds_captured_this_clear += 1
                    self.board[r][c] = " "
                    cleared_cells.add(cell_coord)

        # Clear columns and count diamonds
        for c in columns_to_clear:
            for r in range(self.board_size):
                cell_coord = (r, c)
                if cell_coord not in cleared_cells:
                    if self.board[r][c] == "D":
                        diamonds_captured_this_clear += 1
                    self.board[r][c] = " "
                    cleared_cells.add(cell_coord)

        # Update score based on cleared lines/columns and diamonds
        lines_count = len(lines_to_clear)
        cols_count = len(columns_to_clear)
        base_points = SCORE_BASE_LINE_CLEAR * self.difficulty
        diamond_bonus = SCORE_DIAMOND_BONUS * self.difficulty

        score_gain = (lines_count + cols_count) * base_points
        combo_bonus = max(0, (lines_count + cols_count - 1)) * base_points // SCORE_COMBO_BONUS_DIVISOR
        diamond_points = diamonds_captured_this_clear * diamond_bonus

        self.score += score_gain + combo_bonus + diamond_points
        self.diamonds_collected += diamonds_captured_this_clear

        return diamonds_captured_this_clear # Return diamonds captured in this step

#--------------------------------------------
# Apply a move to create a successor state:

    def apply_move(self, move):
        """
        Applies a placement move (r, c) to the current state and returns the
        NEW resulting GameState. Returns None if the move is invalid.
        """
        if not isinstance(move, tuple) or len(move) != 2:
            print(f"Warning: Invalid move format provided to apply_move: {move}")
            return None

        r, c = move

        # Create a new state based on the current one BEFORE applying the move
        new_state = GameState(
            board=self.board, # Deep copied in __init__
            current_piece=self.current_piece, # Deep copied in __init__
            score=self.score,
            difficulty=self.difficulty,
            cost=self.cost + DEFAULT_MOVE_COST, # Increment cost for the move
            parent=self,
            move=move,
            diamonds_collected=self.diamonds_collected, # Inherit collected count
            total_diamonds=self.total_diamonds
        )

        # 1. Validate the move on the new state's board (redundant if get_possible_moves is used, but safe)
        if not new_state._can_place_piece(r, c):
             # This case should ideally not happen if apply_move is called with a move from get_possible_moves
             # print(f"Warning: apply_move called with invalid move {move} for the state.")
             return None # Move is invalid for this state

        # 2. Place the piece on the new state's board
        new_state._place_piece_on_board(r, c)

        # 3. Check for completed lines/columns on the new state's board and update its score/diamonds
        new_state._check_and_clear_lines_columns()

        # 4. Generate a new piece for the new state (unless game over)
        if new_state.is_game_over():
             new_state.current_piece = None
        else:
             new_state.current_piece = GameState._generate_random_piece(new_state.difficulty)
             # Check if the new piece *can* be placed anywhere. If not, game might be over.
             # This check is often done by the search algorithm or main loop, not necessarily here.
             # if not new_state.get_possible_moves():
             #     # Handle no-moves-left scenario if needed within the state transition
             #     pass

        return new_state

#---------------------------------------------
# Generate successor states:

    def get_successors(self):
        """Generates all possible successor GameState objects from valid moves."""
        successors = []
        possible_moves = self.get_possible_moves()
        for move in possible_moves:
            next_state = self.apply_move(move)
            if next_state: # Ensure apply_move returned a valid state
                successors.append(next_state)
        return successors

#--------------------------------------------
# Path reconstruction:

    def get_path(self):
        """Constructs the path (list of moves) from the initial state to this state."""
        path = []
        current = self
        while current and current.parent is not None: # Stop when current or current.parent is None
            if current.move is not None:
                 path.append(current.move)
            current = current.parent
        path.reverse()
        return path

#--------------------------------------------
# Define goal state:

    def is_goal_state(self):
        """Checks if the goal state is reached (all diamonds collected)."""
        # Goal requires collecting at least one diamond and all available diamonds.
        return self.total_diamonds > 0 and self.diamonds_collected >= self.total_diamonds

#--------------------------------------------
# Define game over state:

    def is_game_over(self):
        """Checks if the game is over (score <= 0)."""
        # Note: Running out of moves is typically checked by the caller (e.g., if get_possible_moves is empty)
        return self.score <= 0

#--------------------------------------------
# --- Special Python Methods (__lt__, __eq__, __hash__) ---

    def __eq__(self, other):
        """Checks equality based on board, piece, and score."""
        if not isinstance(other, GameState):
            return NotImplemented
        # Consider adding diamonds_collected to equality check if needed for specific algorithms
        return (self.board == other.board and
                self.current_piece == other.current_piece and
                self.score == other.score)

    def __hash__(self):
        """Hashes the state based on board, piece, and score."""
        # Using tuples for hashability of nested lists
        board_tuple = tuple(tuple(row) for row in self.board)
        piece_tuple = tuple(tuple(row) for row in self.current_piece) if self.current_piece else None
        # Consider adding diamonds_collected to hash if needed
        return hash((board_tuple, piece_tuple, self.score))

    def __lt__(self, other):
        """Comparison for priority queues (e.g., UCS, A*). Lower cost is better."""
        if not isinstance(other, GameState):
            return NotImplemented
        # Default comparison for algorithms like A* might be based on f-value (cost + heuristic)
        # which is handled externally by heapq. Here, we define a fallback comparison.
        # Let's prioritize lower cost (g-value). If costs are equal, maybe higher score?
        if self.cost != other.cost:
            return self.cost < other.cost
        # Tie-breaking: Higher score might be preferred, but standard heapq doesn't guarantee secondary sort.
        # A simple tie-breaker is often needed for stability. Let's use score.
        return self.score > other.score # Higher score breaks ties (arbitrary choice)

#------------------------------------------------------------
