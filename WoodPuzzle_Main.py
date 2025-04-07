# Date: 2025-04-06
# Version: 1.0
# Author: Ricardo Gonçalves
# Description: Block game where completing a row/column removes it!
# Mechanics: Diamonds, reroll, scoring

#--------------------------------------------


"""
Puzzle game where the player place blocks
on a board to complete rows and columns.

Features:
- Multiple difficulty levels (Easy, Medium, Hard, Expert)
- Variable board sizes (4x4, 5x5, 6x6, 7x7)
- Different piece shapes based on difficulty
- Diamonds for bonus points
- Integration with AI algorithms for hints and automatic gameplay
"""

#------------------------------------------------------------
#Libraries:


import random  
import time    
from game_state import GameState 
from Ai_algorithms import get_ai_move, heuristic_diamond_proximity, heuristic_maximize_score

# For colored output
from colorama import Fore, Style 

#------------------------------------------------------------
#Classes:

class WoodBlockPuzzle:
    """Represents the core of the game, including logic and mechanics."""
#--------------------------------------------
# Modes available for the game:

    def __init__(self, difficulty=1):
        """Initialize the Wood Block Puzzle game with different difficulty levels."""
        self.difficulty = min(max(difficulty, 1), 4)  # Ensure difficulty is between 1 and 4
        self.board_size = 3 + self.difficulty  # Board sizes: 4x4, 5x5, 6x6, 7x7
        self.board = self._create_initial_board()
        self.score = 100 * self.difficulty
        self.current_piece = self.generate_piece()
        self.difficulty_names = ['Easy', 'Medium', 'Hard', 'Expert']
        self.total_diamonds = self._count_diamonds()  # Count diamonds on the board
        self.diamonds_collected = 0  # Initialize the number of diamonds collected
        self.all_diamonds_collected = False  # Initialize the victory condition
        self.selected_heuristic = None  # Initialize the heuristic attribute

#----------------------------------------------------
#Board creation:


    def _create_initial_board(self):
        """Create the initial board based on the difficulty level."""
        # Start with an empty board
        board = [[" " for _ in range(self.board_size)] for _ in range(self.board_size)]

        num_diamonds = max(1, round(0.10 * self.board_size * self.board_size)) # 10% diamantes
        num_obstacles = max(1, round(0.10 * self.board_size * self.board_size)) # 10% obstáculos

        diamonds_placed = 0

        # Placing diamonds on the board
        while diamonds_placed < num_diamonds:
            r = random.randint(0, self.board_size - 1)
            c = random.randint(0, self.board_size - 1)
            #Verify if the position is empty and not an obstacle
            if board[r][c] == " ":
                    board[r][c] = "D"
                    diamonds_placed += 1

        obstacles_placed = 0

        # Placing obstacles on the board
        while obstacles_placed < num_obstacles:
            r = random.randint(0, self.board_size - 1)
            c = random.randint(0, self.board_size - 1)
            if board[r][c] == " ":
                board[r][c] = "#"
                obstacles_placed += 1

        return board


#----------------------------------------------------
#Piece generation:

    def generate_piece(self):
        """Generate a random piece based on difficulty level."""
        # Basic shapes (available at all difficulties)
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
        
        # Combine shapes based on difficulty
        available_shapes = basic_shapes.copy()
        if self.difficulty >= 2:
            available_shapes.extend(medium_shapes)
        if self.difficulty >= 3:
            available_shapes.extend(hard_shapes)
        if self.difficulty >= 4:
            available_shapes.extend(expert_shapes)
        
        return random.choice(available_shapes)
    
#----------------------------------------------------
#Board display:

    def display_board(self):
        """Display the current state of the board with colors."""
        print(f"\nDifficulty: {['Easy', 'Medium', 'Hard', 'Expert'][self.difficulty-1]}")
        print(f"Board Size: {self.board_size}x{self.board_size}")

        # Print column numbers
        print("    " + "   ".join(f"{i}" for i in range(self.board_size)))
        print("   +" + "---+" * self.board_size)

        # Print rows with row numbers
        for i, row in enumerate(self.board):
            row_content = " | ".join(
                f"{Fore.YELLOW + 'D' + Style.RESET_ALL if cell == 'D' else Fore.RED + '#' + Style.RESET_ALL if cell == '#' else ' '}"
                for cell in row
            )
            print(f"{i:2} | {row_content} |")
            print("   +" + "---+" * self.board_size)

        print(f"Score: {self.score}")
        print(f"Diamonds: {self.diamonds_collected}/{self.total_diamonds}\n")

#Piece display:
    def display_piece(self):
        """Display the current piece."""
        print("Current Piece:")
        for row in self.current_piece:
            row_str = "".join("#" if cell == 1 else " " for cell in row)
            print(row_str)
        
        print()

#----------------------------------------------------
#Piece placement:

    def place_piece(self, x, y):
        """
        Places the current piece on the board at position (x, y) and checks if it's valid.
        Generates a new piece after a successful placement.
        """
        try:
            x, y = int(x), int(y)
        except (ValueError, TypeError):
            print("Only numbers are allowed.")
            return False

        piece = self.current_piece
        piece_height, piece_width = len(piece), len(piece[0])

        # Check if the piece fits on the board
        if x < 0 or y < 0 or x + piece_height > self.board_size or y + piece_width > self.board_size:
            print("Invalid move! Out of bounds.")
            return False

        # Check if the cell is occupied by a piece or a diamond
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1 and (self.board[x + i][y + j] != " "):
                    print("Cannot place here! The space is occupied.")
                    return False

        # Place the piece on the board
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:  # where piece has a block == 1
                    self.board[x + i][y + j] = "#"  # Place the piece on the position

        # Penalize for the move
        self.score -= 10 * self.difficulty // 2  # Scaled penalty based on difficulty

        # Generate a new piece after successful placement
        self.current_piece = self.generate_piece()
        print("A new piece has been generated!")

        return True

#----------------------------------------------------
#Check for full lines/columns and pontuation:

    def check_full_lines_and_columns(self):
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

        print(f"Nice! You cleaned {lines_count + cols_count} lines/columns!")
        if diamonds_captured_this_clear > 0:
            print(f"And captured {diamonds_captured_this_clear} diamonds!")
        print(f"You score +{score_gain + combo_bonus + diamond_points} points!")

        # Check if all diamonds have been collected
        if self.diamonds_collected >= self.total_diamonds:
            self.all_diamonds_collected = True

#----------------------------------------------------
#Reroll:

    def reroll(self):
        """Generates a new piece at the player's request."""
        # Penalty based on difficulty level
        penalty = 10 * self.difficulty // 2

        # Check if the player has enough points to reroll
        if self.score < penalty:
            print("You don't have enough points to reroll!")
            return False  # Exit the function without rerolling

        # Deduct points for rerolling
        self.score -= penalty

        # Generate a new piece
        self.current_piece = self.generate_piece()
        print(f"You lost {penalty} points for getting a new piece.")
        return True

#----------------------------------------------------
#Check for diamonds:
    
    def has_diamonds(self):
        """Checks if there are diamonds on the board"""
        for row in self.board:
            if 'D' in row:  
                return True
        return False

#----------------------------------------------------
#Count diamonds:

    def _count_diamonds(self):
        """Counts the total number of diamonds ('D') on the board."""

        count = 0
        for row in self.board:
            count += row.count("D")  
        return count
#----------------------------------------------------
#Game status:

    def get_game_status(self):

        """Creates  a summary of the current game state: difficulty, size, score, diamonds."""
        
        status = f"""
-------------------- Estado do Jogo --------------------
Dificuldade: {self.difficulty_names[self.difficulty-1]} ({self.difficulty})
Tamanho:     {self.board_size}x{self.board_size}
Pontuação:   {self.score}
Diamantes:   {self.diamonds_collected}/{self.total_diamonds}
------------------------------------------------------
"""
        return status

#----------------------------------------------------
#Player input:

    def process_user_move(self, user_input):
        """Processes the player's move based on their input."""
        
        if user_input == 'q':
            return 'quit'  

        elif user_input == 'r':
            if self.reroll():
                return 'success'
            else:
                return 'invalid'

        elif isinstance(user_input, tuple):
            try:
                x, y = user_input
                if self.place_piece(x, y):
                    self.check_full_lines_and_columns()

                    # Check if we won by collecting all diamonds
                    if self.all_diamonds_collected:
                        return 'victory'

                    if self.score <= 0:
                        return 'game_over'
                else:
                    print("Invalid move (could not place the piece). Try again.")
                    return 'invalid'  

            except (ValueError, TypeError):
                print("Unexpected error while processing coordinates.")
                return 'invalid'
        else:
            print("Error: Unrecognized command in process_user_move.")
            return 'invalid'

#----------------------------------------------------
#----------------------------------------------------
# Game introduction text

    def _get_game_intro_text(self):
        """A simple function that returns the welcome text and instructions
            that appear at the start of each game."""
        
        return f"""
=======================================================
Starting New Game - Wood Block Puzzle
=======================================================
Difficulty: {self.difficulty_names[self.difficulty-1]} ({self.difficulty})
Board:      {self.board_size}x{self.board_size}
Objective:  Complete rows/columns, capture DIAMONDS ('D'),
            and keep your score above zero!

Commands:
- Enter 'row column' (e.g., '2 3') to place the piece. Remember its the top-left corner of the piece!
- Enter 'R' to discard the current piece and get a new one (costs points!).
- Enter 'Q' to quit the current game.
======================================================="""

#----------------------------------------------------
# Game over message

    def _display_game_over(self):
            """ Displays the "Game Over" message when the player loses (due to score). """
            print("\n==================== GAME OVER ====================")
            print("You ran out of points!")
            print(f"Final Score: {self.score}")  
            print(f"Diamonds Collected: {self.diamonds_collected}/{self.total_diamonds}")
            print("===================================================")

#----------------------------------------------------
# Victory message

    def _display_victory(self):
        """Displays the 'Victory' message when the player wins by collecting all diamonds."""
        print("\n===================== VICTORY! =====================")
        print(f"Congratulations! You collected all {self.total_diamonds} diamonds!")
        print(f"Final Score: {self.score}")  
        print("====================================================")

#----------------------------------------------------
# Main game loop

    def play(self):
        """
        This function controls the main flow of the game when a HUMAN is playing.
        It is a loop that continues until the game ends.
        """
        # Display the introduction message
        print(self._get_game_intro_text())

        while True:
            self.display_board()
            self.display_piece()

            # Get the player's move
            user_input = input("Your turn! Enter position (row column), 'R' for a new piece, or 'Q' to quit: ").strip()

            # Process input for coordinates
            if user_input.lower() not in ['r', 'q']:
                try:
                    x, y = map(int, user_input.split())
                    user_input = (x, y)
                except ValueError:
                    print("Invalid input! Please enter valid coordinates (row column), 'R', or 'Q'.")
                    continue

            # Process the player's move
            result = self.process_user_move(user_input)

            # Handle the result of the move
            if result == 'quit':
                print("Okay, exiting the current game and returning to the menu...")
                return  # Exit the game loop
            elif result == 'invalid':
                continue  # Let the player try again
            elif result == 'victory':
                self.display_board()
                self._display_victory()  # Display victory message once
                return  # Exit the game loop
            elif result == 'game_over':
                self.display_board()
                self._display_game_over()  # Display game-over message once
                return  # Exit the game loop

#----------------------------------------------------
# AI assistance mode

    def _provide_ai_suggestion(self):
        """
        Provides an AI suggestion for the next move and allows the player to play interactively.
        """
        print("\n--- AI Assistance Mode ---")

        # Define available algorithms
        algorithms = {
            'uninformed': {
                '1': ('bfs', 'BFS (Breadth-First Search)'),
                '2': ('dfs', 'DFS (Depth-First Search)'),
                '3': ('ucs', 'UCS (Uniform Cost Search)'),
                '4': ('dls', 'DLS (Depth-Limited Search)'),
                '5': ('ids', 'IDS (Iterative Deepening Search)')
            },
            'informed': {
                '6': ('greedy', 'Greedy'),
                '7': ('astar', 'A*'),
                '8': ('wastar', 'Weighted A*')
            },
            'cancel': {
                'q': ('cancel', 'Cancel Suggestion')
            }
        }

        print("Choose the algorithm for the suggestion:")

        # Display uninformed algorithms
        print("\nUninformed Algorithms:")
        for key, (_, name) in algorithms['uninformed'].items():
            print(f"{key} - {name}")

        # Display informed algorithms
        print("\nInformed Algorithms:")
        for key, (_, name) in algorithms['informed'].items():
            print(f"{key} - {name}")

        # Display cancel option
        print("\nOther Options:")
        for key, (_, name) in algorithms['cancel'].items():
            print(f"{key} - {name}")

        # Input validation loop
        valid_options = list(algorithms['uninformed'].keys()) + \
                        list(algorithms['informed'].keys()) + \
                        list(algorithms['cancel'].keys())

        while True:
            algo_choice = input("Enter your choice (1-8, q to cancel): ").strip().lower()
            if algo_choice in valid_options:
                break
            else:
                print(f"Invalid input. Please choose one of the following: {', '.join(valid_options)}")

        if algo_choice == 'q':
            print("Suggestion canceled.")
            return  # Exit the function

        # Default to no heuristic (for uninformed search)
        selected_heuristic = None  

        # Determine the selected algorithm
        if algo_choice in algorithms['uninformed']:
            algorithm_code, algorithm_name = algorithms['uninformed'][algo_choice]
        elif algo_choice in algorithms['informed']:
            algorithm_code, algorithm_name = algorithms['informed'][algo_choice]

            # Heuristic selection (only for informed algorithms)
            print("\n--- Choose a Heuristic ---")
            heuristics = {
                '1': ('Maximize Score', heuristic_maximize_score),
                '2': ('Diamond Proximity', heuristic_diamond_proximity)
            }
            for key, (name, _) in heuristics.items():
                print(f"{key} - {name}")

            heuristic_choice = input("Enter your choice (1-2): ").strip()

            # Ensure the heuristic selection is valid
            if heuristic_choice in heuristics:
                selected_heuristic = heuristics[heuristic_choice][1]
            else:
                print("Invalid choice. Using default heuristic (Maximize Score).")
                selected_heuristic = heuristics['1'][1]

        # Main loop for AI assistance
        while True:
            # Display the current board and piece
            self.display_board()
            self.display_piece()

            # Check if the game is over
            if self.score <= 0:
                print("\n--- GAME OVER! ---")
                self._display_game_over()
                break

            if self.all_diamonds_collected:
                print("\n--- VICTORY! ---")
                self._display_victory()
                break

            # Get AI suggestion
            time_limit_suggestion = 5 + self.difficulty
            move = get_ai_move(self, algorithm_code, time_limit_suggestion, selected_heuristic)

            # Handle the case where the AI cannot find a move
            if not move:
                print("\nThe AI could not find a valid move.")
                # Ask the player if they want to reroll
                player_input = input("Do you want to reroll for a new piece? (y/n): ").strip().lower()
                if player_input == 'y':
                    if self.reroll():
                        print("A new piece has been generated.")
                        continue
                    else:
                        print("Failed to reroll. Exiting AI Assistance Mode...")
                        break
                else:
                    print("Reroll declined. Exiting AI Assistance Mode...")
                    break

            # Display AI suggestion
            if isinstance(move, tuple):
                x, y = move
                print(f"\nAI Suggestion: Place piece at position ({x}, {y})")
            else:
                print("\nThe AI returned an unexpected suggestion.")
                break

            # Ask the player if they want to follow the AI's suggestion
            user_input = input("Do you want to follow the AI's suggestion? (y/n/q): ").strip().lower()
            if user_input == 'q':
                print("Exiting AI Assistance Mode...")
                break
            elif user_input == 'y':
                # Execute the AI's suggested move
                if isinstance(move, tuple):
                    x, y = move
                    if self.place_piece(x, y):
                        # Call check_full_lines_and_columns after placing the piece
                        self.check_full_lines_and_columns()
                        # Generate a new piece after the move
                        self.current_piece = self.generate_piece()
                    else:
                        print("Failed to place the piece. Exiting AI Assistance Mode...")
                        break
                else:
                    print("Invalid AI suggestion. Exiting AI Assistance Mode...")
                    break
            elif user_input == 'n':
                # Let the player decide to reroll or make their own move
                player_input = input("Enter 'R' to reroll, 'row column' to place the piece, or 'Q' to quit: ").strip().lower()
                if player_input == 'q':
                    print("Exiting AI Assistance Mode...")
                    break
                elif player_input == 'r':
                    if self.reroll():
                        print("A new piece has been generated.")
                        continue
                    else:
                        print("Failed to reroll. Exiting AI Assistance Mode...")
                        break
                else:
                    try:
                        x, y = map(int, player_input.split())
                        if self.place_piece(x, y):
                            # Call check_full_lines_and_columns after placing the piece
                            self.check_full_lines_and_columns()
                            # Generate a new piece after the move
                            self.current_piece = self.generate_piece()
                        else:
                            print("Invalid move. Try again.")
                    except ValueError:
                        print("Invalid input. Please enter valid coordinates (row column), 'R', or 'Q'.")
            else:
                print("Invalid input. Please enter 'y', 'n', or 'q'.")


#----------------------------------------------------
# AI play alone mode

    def play_with_ai(self, algorithm_code, selected_heuristic, time_limit_per_move=10):
        """
        Allows the AI to play the game alone using the specified algorithm and heuristic.
        """
        print("\n--- AI Playing Alone Mode ---")
        print(f"Using Algorithm: {algorithm_code.upper()}")
        if selected_heuristic:
            print(f"Using Heuristic: {selected_heuristic.__name__}")
        else:
            print("Using Heuristic: None (Uninformed Algorithm)")
        print(f"Time Limit Per Move: {time_limit_per_move} seconds\n")

        move_count = 0  # Track the number of moves
        start_time = time.time()  # Track the start time

        while True:
            # Check if the game is over before displaying the board
            if self.score <= 0:
                print("\n--- GAME OVER! ---")
                self._display_game_over()
                break

            # Check if all diamonds have been collected (victory condition)
            if self.all_diamonds_collected:
                break  # Exit the loop if victory condition is met

            while True:  # Keep rerolling if there's no valid move and the score allows it
                move = get_ai_move(self, algorithm_code, time_limit_per_move, selected_heuristic)
                
                if move:
                    break  # Valid move found, exit reroll loop
                
                # If no move was found and a reroll is possible, perform a reroll
                if self.score > 0:
                    print("\nNo valid move found. Rerolling...")
                    self.reroll()
                else:
                    print("\nNo valid move found and reroll is not possible. Exiting AI Play Mode...")
                    return  # Exit if rerolling is not allowed

            # Execute the AI's suggested move
            if isinstance(move, tuple):
                x, y = move
                print(f"\nAI Move {move_count + 1}: Place piece at position ({x}, {y})")
                if self.place_piece(x, y):
                    # Call check_full_lines_and_columns after placing the piece
                    self.check_full_lines_and_columns()
                    # Generate a new piece after the move
                    self.current_piece = self.generate_piece()
                    move_count += 1
                else:
                    print("Failed to place the piece. Exiting AI Play Mode...")
                    break   

        # Calculate and display the total time taken
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n--- AI Play Summary ---")
        print(f"Total Moves: {move_count}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Final Score: {self.score}")
        print(f"Diamonds Collected: {self.diamonds_collected}/{self.total_diamonds}")
        print("-----------------------")

        # Print victory message if all diamonds were collected
        if self.all_diamonds_collected:
            self._display_victory()

    def _play_with_ai_mode(self):
        """
        Allows the user to select an algorithm and lets the AI play the game alone.
        """
        print("\n--- AI Play Alone Mode ---")

        # Define available algorithms
        algorithms = {
            'uninformed': {
                '1': ('bfs', 'BFS (Breadth-First Search)'),
                '2': ('dfs', 'DFS (Depth-First Search)'),
                '3': ('ucs', 'UCS (Uniform Cost Search)'),
                '4': ('dls', 'DLS (Depth-Limited Search)'),
                '5': ('ids', 'IDS (Iterative Deepening Search)')
            },
            'informed': {
                '6': ('greedy', 'Greedy'),
                '7': ('astar', 'A*'),
                '8': ('wastar', 'Weighted A*')
            },
            'cancel': {
                'q': ('cancel', 'Cancel AI Play')
            }
        }

        # Display uninformed algorithms
        print("\nUninformed Algorithms:")
        for key, (_, name) in algorithms['uninformed'].items():
            print(f"{key} - {name}")

        # Display informed algorithms
        print("\nInformed Algorithms:")
        for key, (_, name) in algorithms['informed'].items():
            print(f"{key} - {name}")

        # Display cancel option
        print("\nOther Options:")
        for key, (_, name) in algorithms['cancel'].items():
            print(f"{key} - {name}")

        # Input validation loop
        valid_options = list(algorithms['uninformed'].keys()) + \
                        list(algorithms['informed'].keys()) + \
                        list(algorithms['cancel'].keys())

        while True:
            algo_choice = input("Enter your choice (1-8, q to cancel): ").strip().lower()
            if algo_choice in valid_options:
                break
            else:
                print(f"Invalid input. Please choose one of the following: {', '.join(valid_options)}")

        if algo_choice == 'q':
            print("AI Play canceled. Returning to the main menu...")
            return  # Exit the function

        # Determine the selected algorithm
        if algo_choice in algorithms['uninformed']:
            algorithm_code, algorithm_name = algorithms['uninformed'][algo_choice]
            selected_heuristic = None  # No heuristic needed for uninformed algorithms
        elif algo_choice in algorithms['informed']:
            algorithm_code, algorithm_name = algorithms['informed'][algo_choice]

            # Heuristic selection (only for informed algorithms)
            print("\n--- Choose a Heuristic ---")
            heuristics = {
                '1': ('Maximize Score', heuristic_maximize_score),
                '2': ('Diamond Proximity', heuristic_diamond_proximity)
            }
            for key, (name, _) in heuristics.items():
                print(f"{key} - {name}")

            heuristic_choice = input("Enter your choice (1-2): ").strip()
            if heuristic_choice not in heuristics:
                print("Invalid choice. Using default heuristic (Maximize Score).")
                selected_heuristic = heuristics['1'][1]
            else:
                selected_heuristic = heuristics[heuristic_choice][1]

        # Define parameters for the AI to play alone
        time_limit_move = 5 + (self.difficulty * 2)  # Time limit per MOVE (increases with difficulty)

        print(f"\nStarting automatic game with {algorithm_name}...")
        self.play_with_ai(algorithm_code, selected_heuristic, time_limit_move)

        input("\nPress Enter to return to the main menu...")

#-----------------------------------------------------
#Main:

if __name__ == "__main__":
    running = True

    random.seed()

    while running:
        print("\n===== Wood Block Puzzle AI Edition =====")
        print("1 - Play (Human)")
        print("2 - Play with AI Assistance")
        print("3 - Let the AI Play Alone")
        print("Q - Exit the Game")
        print("========================================")

        choice = input("Choose an option (1-3, Q): ").strip().lower()
        if choice not in ['1', '2', '3', 'q']:
            print("Invalid option. Please choose 1, 2, 3, or Q.")
            continue

        if choice == 'q':
            print("\nThank you for playing! See you next time.")
            running = False  
            continue  

        if choice in ['1', '2', '3']:
            print("\n--- Select Difficulty ---")
            print("1 - Easy (4x4)")
            print("2 - Medium (5x5)")
            print("3 - Hard (6x6)")
            print("4 - Expert (7x7)")
            print("Q - Return to Menu")
            print("-------------------------------")

            diff_choice_input = input("Enter difficulty (1-4, Q): ").strip().lower()
            if diff_choice_input not in ['1', '2', '3', '4', 'q']:
                print("Invalid option. Please choose 1, 2, 3, 4, or Q.")
                continue

            if diff_choice_input == 'q':
                continue  

            try:
                difficulty = int(diff_choice_input)
                if not 1 <= difficulty <= 4:
                    print("Invalid difficulty.")
                    continue  
            except ValueError:
                print("Invalid difficulty input.")
                continue  

            game = WoodBlockPuzzle(difficulty)

            if choice == '1':
                game.play()
            elif choice == '2':
                game._provide_ai_suggestion()
            elif choice == '3':
                game._play_with_ai_mode()





