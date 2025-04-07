# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Implementation of GameState Class for Wood Block Puzzle Game

#--------------------------------------------

#Libraries:
import copy 
import random 

#--------------------------------------------
#Classes:

class GameState:
    """
    Represents a state (a snapshot) of the game to be used by AI algorithms.
    """
#--------------------------------------------
#Constructs a GameState object with the current board, piece, and score:

    def __init__(self, board, current_piece, score, difficulty=1, cost=0, parent=None, move=None):
        """
        Initializes a GameState object with the current board, piece, score, difficulty, cost, and parent.

        Args:
            board (list): The current state of the game board.
            current_piece (list): The current piece to be placed.
            score (int): The current score of the game.
            difficulty (int): The difficulty level of the game (default is 1).
            cost (int): The cumulative cost to reach this state (default is 0).
            parent (GameState): The parent state that led to this state (default is None).
            move (tuple): The move (e.g., (x, y)) that led to this state.
        """
        # Deep copy to ensure independence from the original game state
        self.board = copy.deepcopy(board)
        self.current_piece = copy.deepcopy(current_piece)
        self.score = score
        self.difficulty = difficulty
        self.cost = cost  # Initialize the cost attribute
        self.parent = parent  # Reference to the parent state
        self.move = move  # Store the move that led to this state

        # Initialize depth
        self.depth = parent.depth + 1 if parent else 0  # Depth is 0 for the initial state

        # Initialize board size
        self.board_size = len(board)  # Derive board size from the dimensions of the board

        # Counters specific to this state
        self.diamonds_collected = 0
        self.total_diamonds = sum(row.count("D") for row in board)
        self.new_pieces_requested = 0

#--------------------------------------------
# Possible moves:

    def get_possible_moves(self):
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
# Check for piece fitness in board

    def _can_place_piece(self, x, y):
        """
        Checks if the current piece can be placed at position (x, y) on the board.
        """
        piece = self.current_piece

        if not piece:
            return False

        piece_height, piece_width = len(piece), len(piece[0])

        # Check if the piece fits within the board boundaries
        if x < 0 or y < 0 or x + piece_height > self.board_size or y + piece_width > self.board_size:
            return False

        # Check each cell of the piece
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:  # Occupied cell in the piece
                    board_cell = self.board[x + i][y + j]
                    if board_cell == "#" or board_cell == "D":  # Blocked or diamond cell
                        return False

        return True

#--------------------------------------------
    def place_piece(self, x, y):
        """
        Simulates placing the current piece on the board at position (x, y).
        Returns True if the placement is valid, False otherwise.
        """
        piece = self.current_piece

        if not piece:
            return False

        piece_height, piece_width = len(piece), len(piece[0])

        # Check if the piece fits within the board boundaries
        if x < 0 or y < 0 or x + piece_height > self.board_size or y + piece_width > self.board_size:
            return False

        # Check for collisions
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:  # Occupied cell in the piece
                    board_cell = self.board[x + i][y + j]
                    if board_cell == "#" or board_cell == "D":  # Blocked or diamond cell
                        return False

        # Place the piece on the board
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:
                    self.board[x + i][y + j] = "#"

        # Update the score (penalty for placing a piece)
        self.score -= 10

        return True

#--------------------------------------------
# Apply specific move:

    def apply_move(self, move):
        """
        Applies a specific move to this state and returns the NEW resulting state.
        """
        # Create a new state (board, piece, score, and cost)
        new_state = GameState(self.board, self.current_piece, self.score, self.difficulty, self.cost, parent=self, move=move)

        # Copy state-specific counters
        new_state.diamonds_collected = self.diamonds_collected
        new_state.total_diamonds = self.total_diamonds

        # Handle placement moves
        if isinstance(move, tuple) and len(move) == 2:
            x, y = move

            if not new_state.place_piece(x, y):
                return None

            new_state._check_full_lines_and_columns()

            # Increment the cost (e.g., fixed cost per move)
            new_state.cost += 1  # Increment cost by 1 for each move

            if new_state.score > 0:
                new_state.current_piece = self._generate_new_piece(self.difficulty)
            else:
                new_state.current_piece = None
                return new_state

            return new_state

        else:
            print(f"Warning: Attempt to apply an unknown move type: {move}")
            return None
#---------------------------------------------
#Possible states:

    def get_successors(self):
        """
        Generates all possible successor states by placing the current piece on the board.
        Returns:
            list: A list of successor GameState objects.
        """
        successors = []
        possible_moves = self.get_possible_moves()
        for move in possible_moves:
            x, y = move
            # Create a deep copy of the board to avoid modifying the current state
            new_board = [row[:] for row in self.board]
            new_state = GameState(
                board=new_board,
                current_piece=self.current_piece,
                score=self.score,
                difficulty=self.difficulty,
                cost=self.cost + 1,  # Increment cost for the new state
                parent=self,
                move=move  # Set the move that led to this state
            )
            if new_state.place_piece(x, y):  # Place the piece and validate the move
                new_state.check_full_lines_and_columns()  # Update the board and score
                # Use the private `_generate_new_piece` method to generate a new piece
                new_state.current_piece = new_state._generate_new_piece(self.difficulty)
                successors.append(new_state)
        return successors

#--------------------------------------------
    def get_path(self):
        """
        Constructs the path from the initial state to the current state.
        Returns:
            list: A list of moves (e.g., [(x1, y1), (x2, y2), ...]) that led to this state.
        """
        path = []
        current = self
        while current.parent is not None:
            path.append(current.move)  # Add the move that led to the current state
            current = current.parent
        path.reverse()  # Reverse the path to start from the initial state
        return path

#--------------------------------------------
# Generate new piece:

    def _generate_new_piece(self, difficulty):

        """Generate a random piece based on difficulty level.
        Pieces are represented as a list of lists representing a matrix"""

        basic_shapes = [
            [[1, 1]],     
            [[1], [1]], 
            [[1, 1, 1]],   
            [[1], [1], [1]]
        ]
        
        # Medium shapes (available at difficulty 2+)
        medium_shapes = [
            [[1, 1], [1, 1]],  
            [[1, 1], [1, 0]],  # L shape
            [[1, 1], [0, 1]],  # Reversed L shape
            [[1, 0], [1, 1]]   # L shape rotated
        ]
        
        # Hard shapes (available at difficulty 3+)
        hard_shapes = [
            [[1, 1, 1], [1, 0, 0]],  # L shape long
            [[1, 1, 1], [0, 0, 1]],  # Reversed L shape long
            [[1, 0], [1, 0], [1, 1]] # L shape rotated long
        ]
        
        # Expert shapes (only at difficulty 4)
        expert_shapes = [
            [[1, 1, 1], [0, 1, 0]],  # T shape
            [[0, 1, 0], [1, 1, 1]],  # Inverted T shape
            [[1, 1, 0], [0, 1, 1]]   # Z shape
        ]
        
        # [:] makes a shallow copy of the list
        available_shapes = basic_shapes[:] 
        # If difficulty high enough, add more complex pieces
        if difficulty >= 2:
            available_shapes.extend(medium_shapes)
        if difficulty >= 3:
            available_shapes.extend(hard_shapes)
        if difficulty >= 4:
            available_shapes.extend(expert_shapes)
        
        # Randomly select a shape from the available shapes
        return random.choice(available_shapes) 

#--------------------------------------------
# Check for full lines and columns:

    def _check_full_lines_and_columns(self):
        """Checks if there are complete lines or columns on the board and clears them.
           Also captures diamonds and adds points."""
        
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

        # If there are no lines or columns to clear, exit the function
        if not lines_to_clear and not columns_to_clear:
            return 

        cleared_cells = set()

        # Clear the lines
        for r in lines_to_clear:
            for c in range(self.board_size):
                cell_coord = (r, c) 
                if cell_coord not in cleared_cells:
                    if self.board[r][c] == "D":
                        diamonds_captured_this_clear += 1 
                    self.board[r][c] = " "
                    cleared_cells.add(cell_coord)

        # Clear the columns
        for c in columns_to_clear:
            for r in range(self.board_size):
                cell_coord = (r, c)
                if cell_coord not in cleared_cells:
                    if self.board[r][c] == "D":
                        diamonds_captured_this_clear += 1
                    self.board[r][c] = " "
                    cleared_cells.add(cell_coord)

        # Points calculation
        lines_count = len(lines_to_clear)
        cols_count = len(columns_to_clear) 

        base_points = 50 * self.difficulty
        diamond_bonus = 100 * self.difficulty

        score_gain = (lines_count + cols_count) * base_points
        combo_bonus = max(0, (lines_count + cols_count - 1)) * base_points // 2
        diamond_points = diamonds_captured_this_clear * diamond_bonus
        self.score += score_gain + combo_bonus + diamond_points
        self.diamonds_collected += diamonds_captured_this_clear


#--------------------------------------------
# Define goal state:
    def is_goal_state(self):
        return self.total_diamonds > 0 and self.diamonds_collected >= self.total_diamonds and self.score > 0


#--------------------------------------------

# --- Special Python Methods (__lt__, __eq__, __hash__) ---
# These methods help Python compare and store GameStates

#--------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.board == other.board and self.current_piece == other.current_piece and self.score == other.score

    def __hash__(self):
        return hash((tuple(tuple(row) for row in self.board), tuple(tuple(row) for row in self.current_piece), self.score))

    def __lt__(self, other):
        my_priority = (-self.score, -self.diamonds_collected)
        other_priority = (-other.score, -other.diamonds_collected)
        return my_priority < other_priority

#------------------------------------------------------------




