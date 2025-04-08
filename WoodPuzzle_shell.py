# Date: 2025-04-07
# Version: 1.2
# Author: Ricardo Gonçalves (rdtg94)
# Description: Main file for Wood Block Puzzle game with AI integration.

#------------------------------------------------------------
#Libraries:

import random
import time
import math # For rounding percentages
from game_state import GameState # GameState now handles piece generation logic
# Import AI functions and the available heuristics
from Ai_algorithms import get_ai_move, heuristic_diamond_proximity, heuristic_maximize_score

# Import constants
from constants import *

# For colored output (optional, ensure colorama is installed: pip install colorama)
try:
    from colorama import Fore, Style, init
    init(autoreset=True) # Automatically reset style after each print
except ImportError:
    print("Colorama not found, installing...")
    try:
        import subprocess
        subprocess.check_call(['pip', 'install', 'colorama'])
        from colorama import Fore, Style, init
        init(autoreset=True)
    except Exception as e:
        print(f"Could not install or import colorama. Output will not be colored. Error: {e}")
        # Define dummy Fore and Style objects if colorama fails
        class DummyStyle:
            def __getattr__(self, name):
                return ""
        Fore = DummyStyle()
        Style = DummyStyle()


#------------------------------------------------------------
#Classes:

class WoodBlockPuzzle:
    """Represents the core game logic, UI, and interaction."""
#--------------------------------------------
# Initialize game:

    def __init__(self, difficulty=1):
        """Initialize the game."""
        self.difficulty = min(max(difficulty, 1), 4) # Clamp difficulty 1-4
        self.board_size = BOARD_SIZE_BASE + self.difficulty
        self.board = self._create_initial_board()
        self.score = 100 * self.difficulty # Initial score based on difficulty
        # Use GameState's static method to generate the first piece
        self.current_piece = GameState._generate_random_piece(self.difficulty)
        self.difficulty_names = ['Easy', 'Medium', 'Hard', 'Expert']
        self.total_diamonds = self._count_diamonds()
        self.diamonds_collected = 0
        self.all_diamonds_collected = (self.total_diamonds == 0) # True if no diamonds initially
        self.selected_heuristic = None # For AI modes

#----------------------------------------------------
#Board creation:

    def _create_initial_board(self):
        """Create the initial board with obstacles and diamonds."""
        board = [[" " for _ in range(self.board_size)] for _ in range(self.board_size)]
        total_cells = self.board_size * self.board_size

        # Calculate number of diamonds and obstacles based on percentages
        num_diamonds = max(MIN_DIAMONDS, math.floor(DIAMOND_PERCENTAGE * total_cells))
        num_obstacles = max(MIN_OBSTACLES, math.floor(OBSTACLE_PERCENTAGE * total_cells))

        # Ensure we don't try to place more items than available empty cells
        if num_diamonds + num_obstacles >= total_cells:
            print("Warning: High density of diamonds/obstacles requested, may fill board.")
            num_obstacles = max(0, total_cells - num_diamonds - 1) # Adjust obstacles

        # Get all possible coordinates
        all_coords = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
        random.shuffle(all_coords)

        # Place diamonds
        placed_count = 0
        coords_iterator = iter(all_coords)
        try:
            while placed_count < num_diamonds:
                r, c = next(coords_iterator)
                board[r][c] = "D"
                placed_count += 1
        except StopIteration:
             print("Warning: Ran out of cells while placing diamonds.")


        # Place obstacles in remaining shuffled coordinates
        obstacles_placed = 0
        try:
             while obstacles_placed < num_obstacles:
                  r, c = next(coords_iterator)
                  # Ensure we don't overwrite a diamond (shouldn't happen with iterator, but safe check)
                  if board[r][c] == " ":
                       board[r][c] = "#"
                       obstacles_placed += 1
        except StopIteration:
             print("Warning: Ran out of cells while placing obstacles.")


        return board

#----------------------------------------------------
# Piece generation (delegated):

    def generate_piece(self):
        """Generates a new piece using the GameState's static method."""
        return GameState._generate_random_piece(self.difficulty)

#----------------------------------------------------
#Board display:

    def display_board(self):
        """Display the current state of the board with colors."""
        print(f"\n--- Difficulty: {self.difficulty_names[self.difficulty-1]} | Score: {self.score} | Diamonds: {self.diamonds_collected}/{self.total_diamonds} ---")

        # Print column numbers
        print("    " + "   ".join(f"{i}" for i in range(self.board_size)))
        print("   +" + "---+" * self.board_size)

        # Print rows with row numbers and colored cells
        for i, row in enumerate(self.board):
            row_str = []
            for cell in row:
                if cell == 'D':
                    row_str.append(f"{Fore.YELLOW + 'D' + Style.RESET_ALL}")
                elif cell == '#':
                    # Use a different color for placed pieces vs obstacles if desired
                    # For now, obstacles and placed pieces look the same
                    row_str.append(f"{Fore.RED + '#' + Style.RESET_ALL}")
                else:
                    row_str.append(' ') # Empty cell
            row_content = " | ".join(row_str)
            print(f"{i:2} | {row_content} |")
            print("   +" + "---+" * self.board_size)
        print("-" * (4 + 4 * self.board_size)) # Footer line

#----------------------------------------------------
# Piece display:

    def display_piece(self):
        """Display the current piece."""
        if not self.current_piece:
            print("No current piece.")
            return
        print("\nCurrent Piece:")
        for row in self.current_piece:
            # Use a different color for the current piece
            row_str = "".join(f"{Fore.CYAN + '#' + Style.RESET_ALL}" if cell == 1 else " " for cell in row)
            print(row_str)
        print()

#----------------------------------------------------
# Piece placement (for Human Player):

    def place_piece(self, r_in, c_in):
        """
        Handles HUMAN player placing the current piece at (r, c).
        Validates move, updates board, applies penalty, generates new piece.
        Returns True if successful, False otherwise.
        """
        try:
            r, c = int(r_in), int(c_in)
        except (ValueError, TypeError):
            print(f"{Fore.RED}Invalid input. Please enter row and column numbers.{Style.RESET_ALL}")
            return False

        if not self.current_piece:
            print(f"{Fore.RED}Error: No piece available to place.{Style.RESET_ALL}")
            return False

        piece = self.current_piece
        piece_height, piece_width = len(piece), len(piece[0])

        # 1. Boundary Check
        if r < 0 or c < 0 or r + piece_height > self.board_size or c + piece_width > self.board_size:
            print(f"{Fore.RED}Invalid move: Piece out of bounds.{Style.RESET_ALL}")
            return False

        # 2. Collision Check
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1 and self.board[r + i][c + j] != " ":
                    print(f"{Fore.RED}Invalid move: Space occupied at ({r + i}, {c + j}).{Style.RESET_ALL}")
                    return False

        # 3. Place the piece on the live board
        for i in range(piece_height):
            for j in range(piece_width):
                if piece[i][j] == 1:
                    self.board[r + i][c + j] = "#" # Mark as placed piece

        # 4. Apply penalty
        penalty = SCORE_PENALTY_PLACE_PIECE # Use constant
        self.score -= penalty
        # print(f"Placed piece. Score penalized by {penalty}.") # Optional feedback

        # 5. Check for full lines/columns (handled AFTER placement by the main loop)
        # self.check_full_lines_and_columns() # This is called separately now

        # 6. Generate a new piece for the player
        self.current_piece = self.generate_piece()
        # print("New piece generated.") # Optional feedback

        # 7. Check if the new piece has any valid moves (Game Over condition)
        if not self._has_valid_moves(self.current_piece):
             print(f"{Fore.RED}The new piece has no valid moves!{Style.RESET_ALL}")
             # The game over check based on score or no moves happens in the main loop

        return True

#----------------------------------------------------
# Check if a given piece has any valid moves on the current board

    def _has_valid_moves(self, piece_to_check):
        """Checks if the provided piece can be placed anywhere on the current board."""
        if not piece_to_check: return False
        piece_height, piece_width = len(piece_to_check), len(piece_to_check[0])

        for r in range(self.board_size - piece_height + 1):
            for c in range(self.board_size - piece_width + 1):
                can_place = True
                # Boundary check (already handled by loop range)
                # Collision check
                for i in range(piece_height):
                    for j in range(piece_width):
                        if piece_to_check[i][j] == 1:
                            if self.board[r + i][c + j] != " ":
                                can_place = False
                                break
                    if not can_place: break
                if can_place:
                    return True # Found at least one valid move
        return False # No valid moves found for this piece

#----------------------------------------------------
# Check for full lines/columns and update score (for Live Game)

    def check_full_lines_and_columns(self):
        """
        Checks for full lines/columns on the LIVE board, clears them,
        updates score, and counts collected diamonds.
        NOTE: GameState has similar logic for simulation. Keep synchronized.
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
            return # Nothing to clear

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

        total_gain = score_gain + combo_bonus + diamond_points
        self.score += total_gain
        self.diamonds_collected += diamonds_captured_this_clear

        # Provide feedback
        if lines_count + cols_count > 0:
             print(f"{Fore.GREEN}Cleared {lines_count} line(s) and {cols_count} column(s)!{Style.RESET_ALL}")
             if diamonds_captured_this_clear > 0:
                  print(f"{Fore.YELLOW}Captured {diamonds_captured_this_clear} diamond(s)!{Style.RESET_ALL}")
             print(f"Score +{total_gain} points!")

        # Check victory condition
        if self.total_diamonds > 0 and self.diamonds_collected >= self.total_diamonds:
            self.all_diamonds_collected = True


#----------------------------------------------------
# Reroll piece:

    def reroll(self):
        """Generates a new piece for the player, applying a penalty."""
        penalty = SCORE_PENALTY_REROLL_FACTOR * self.difficulty # Scaled penalty

        if self.score < penalty:
            print(f"{Fore.RED}Not enough points ({self.score}) to reroll (costs {penalty}).{Style.RESET_ALL}")
            return False

        self.score -= penalty
        self.current_piece = self.generate_piece()
        print(f"Rerolled piece. Score -{penalty} points.")

        # Check if the new piece has any valid moves
        if not self._has_valid_moves(self.current_piece):
             print(f"{Fore.RED}The new piece (after reroll) also has no valid moves!{Style.RESET_ALL}")
             # Game might end soon if score is also low

        return True

#----------------------------------------------------
# Count diamonds:

    def _count_diamonds(self):
        """Counts the total number of diamonds ('D') initially on the board."""
        return sum(row.count("D") for row in self.board)

#----------------------------------------------------
# Game status summary:

    def get_game_status(self):
        """Returns a string summary of the current game state."""
        status = f"""
-------------------- Game Status --------------------
Difficulty: {self.difficulty_names[self.difficulty-1]} ({self.difficulty})
Board Size: {self.board_size}x{self.board_size}
Score:      {self.score}
Diamonds:   {self.diamonds_collected}/{self.total_diamonds}
------------------------------------------------------
"""
        return status

#----------------------------------------------------
# Process human player input:

    def process_user_move(self, user_input):
        """Processes the player's input ('r', 'q', or coordinates)."""
        action = user_input.strip().lower()

        if action == 'q':
            return 'quit'

        elif action == 'r':
            if self.reroll():
                return 'rerolled' # Indicate success
            else:
                return 'invalid' # Indicate failure (not enough points)

        else:
            # Try to parse coordinates
            try:
                parts = action.split()
                if len(parts) != 2:
                    raise ValueError("Input must be two numbers separated by space.")
                r, c = map(int, parts)

                if self.place_piece(r, c):
                    # Placement successful, now check lines/columns
                    self.check_full_lines_and_columns()

                    # Check game end conditions after placement and line clearing
                    if self.all_diamonds_collected:
                        return 'victory'
                    if self.score <= 0:
                        return 'game_over_score'
                    if not self._has_valid_moves(self.current_piece):
                         # Check score again, maybe reroll helped avoid immediate game over
                         if self.score <= 0:
                              return 'game_over_score'
                         else:
                              # Score is positive, but no moves left for the NEW piece
                              return 'game_over_no_moves'

                    return 'placed' # Move successful

                else:
                    # place_piece returned False (invalid placement)
                    return 'invalid'

            except ValueError as e:
                print(f"{Fore.RED}Invalid input: {e}. Use 'row col', 'r', or 'q'.{Style.RESET_ALL}")
                return 'invalid'
            except Exception as e:
                 print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
                 return 'invalid'

#----------------------------------------------------
# Game introduction text:

    def _get_game_intro_text(self):
        """Returns the introductory text for the game."""
        return f"""
=======================================================
        Wood Block Puzzle - AI Edition
        Developed by: Ricardo Gonçalves (rdtg94)
=======================================================
Difficulty: {self.difficulty_names[self.difficulty-1]} ({self.difficulty})
Board:      {self.board_size}x{self.board_size}
Objective:  Complete rows/columns by placing pieces.
            Capture all {Fore.YELLOW}DIAMONDS ('D'){Style.RESET_ALL} to win!
            Keep your score above zero. Avoid blocking yourself!
            ({Fore.RED}'#'{Style.RESET_ALL} are obstacles or placed pieces)

Commands:
- Enter 'row col' (e.g., '2 3') to place the {Fore.CYAN}current piece{Style.RESET_ALL}'s top-left corner.
- Enter 'r' to discard the current piece and get a new one (costs points!).
- Enter 'q' to quit the current game.
======================================================="""

#----------------------------------------------------
# Game over messages:

    def _display_game_over(self, reason="score"):
        """ Displays the 'Game Over' message. """
        print(Fore.RED + "\n==================== GAME OVER ====================")
        if reason == "score":
            print("          You ran out of points!")
        elif reason == "no_moves":
             print("     No valid moves left for the current piece!")
        else:
             print("              Game ended.")
        print(f"Final Score: {self.score}")
        print(f"Diamonds Collected: {self.diamonds_collected}/{self.total_diamonds}")
        print("===================================================" + Style.RESET_ALL)

#----------------------------------------------------
# Victory message:

    def _display_victory(self):
        """Displays the 'Victory' message."""
        print(Fore.GREEN + "\n===================== VICTORY! =====================")
        print(f"Congratulations! You collected all {self.total_diamonds} diamonds!")
        print(f"Final Score: {self.score}")
        print("====================================================" + Style.RESET_ALL)

#----------------------------------------------------
# Main game loop (Human Player):

    def play(self):
        """Controls the main game flow for a human player."""
        print(self._get_game_intro_text())

        game_running = True
        while game_running:
            self.display_board()
            self.display_piece()

            # Check for immediate game over condition (no moves for current piece)
            # This check happens *before* player input if the previous move resulted in this state
            if not self._has_valid_moves(self.current_piece):
                 print(f"{Fore.RED}No valid moves available for the current piece!{Style.RESET_ALL}")
                 # Offer reroll if possible, otherwise game might end
                 reroll_cost = SCORE_PENALTY_REROLL_FACTOR * self.difficulty
                 if self.score > reroll_cost:
                      print(f"You might want to reroll ('r' - costs {reroll_cost}).")
                 else:
                      print(f"Not enough points ({self.score}) to reroll (costs {reroll_cost}). Game might be over.")
                      # Let the input process handle potential game over based on score too
                      pass # Proceed to input, maybe player quits

            # Get player input
            user_input = input("Enter move ('row col'), 'r' (reroll), or 'q' (quit): ")

            # Process the input
            result = self.process_user_move(user_input)

            # Handle results
            if result == 'quit':
                print("Exiting game...")
                game_running = False
            elif result == 'victory':
                self.display_board() # Show final board
                self._display_victory()
                game_running = False
            elif result == 'game_over_score':
                self.display_board()
                self._display_game_over(reason="score")
                game_running = False
            elif result == 'game_over_no_moves':
                 # This state is tricky. Player has score > 0 but no moves for the current piece.
                 # Reroll might have been attempted and failed, or player didn't reroll.
                 self.display_board()
                 self._display_game_over(reason="no_moves")
                 game_running = False
            elif result == 'placed':
                # Piece placed successfully, loop continues
                pass
            elif result == 'rerolled':
                # Reroll successful, loop continues (board/piece will be redisplayed)
                pass
            elif result == 'invalid':
                # Invalid input or move, loop continues
                print(f"{Fore.YELLOW}Please try again.{Style.RESET_ALL}")
                pass

        print("\nReturning to main menu.")

#----------------------------------------------------
# AI Assistance Mode:

    def _provide_ai_suggestion(self):
        """Provides AI suggestions interactively."""
        print(Fore.MAGENTA + "\n--- AI Assistance Mode ---" + Style.RESET_ALL)

        algorithm_code, selected_heuristic_func = self._select_ai_algorithm_and_heuristic()
        if algorithm_code is None:
            return # User cancelled selection

        time_limit_suggestion = AI_SUGGESTION_TIME_LIMIT_BASE + (self.difficulty * AI_TIME_LIMIT_DIFFICULTY_MULTIPLIER // 2)

        game_running = True
        while game_running:
            self.display_board()
            self.display_piece()

            # Check for game end conditions before getting AI move
            if self.all_diamonds_collected:
                self._display_victory()
                break
            if self.score <= 0:
                self._display_game_over("score")
                break
            if not self._has_valid_moves(self.current_piece):
                 print(f"{Fore.RED}No valid moves available for the current piece!{Style.RESET_ALL}")
                 # In assistance mode, let's see if AI suggests reroll or if player wants to
                 ai_move = None # Force AI to reconsider or player to act
            else:
                 # Get AI suggestion
                 ai_move = get_ai_move(self, algorithm_code, time_limit_suggestion, selected_heuristic_func)


            if ai_move:
                r, c = ai_move
                print(f"{Fore.CYAN}AI Suggestion ({algorithm_code.upper()}): Place piece at ({r}, {c}){Style.RESET_ALL}")
                user_choice = input("Follow suggestion? (y/n), make own move ('row col'), reroll ('r'), or quit ('q'): ").strip().lower()

                if user_choice == 'y':
                    result = self.process_user_move(f"{r} {c}") # Process AI's move
                elif user_choice == 'n':
                    continue # Let loop redisplay and ask again (or player makes own move next)
                elif user_choice == 'q':
                     game_running = False
                     continue
                elif user_choice == 'r':
                     result = self.process_user_move('r')
                else:
                     # Assume user entered coordinates or invalid input
                     result = self.process_user_move(user_choice) # Process player's own move/input

            else: # AI could not find a move OR no moves were possible initially
                if self._has_valid_moves(self.current_piece): # Check again in case AI just failed
                     print(f"{Fore.YELLOW}AI ({algorithm_code.upper()}) could not find a valid move suggestion.{Style.RESET_ALL}")
                # If no moves were possible, message was already printed
                user_choice = input("No AI suggestion. Reroll ('r'), make own move ('row col'), or quit ('q'): ").strip().lower()
                result = self.process_user_move(user_choice) # Process player's action

            # Handle results after player/AI action
            if result == 'quit':
                game_running = False
            elif result == 'victory':
                self.display_board()
                self._display_victory()
                game_running = False
            elif result == 'game_over_score':
                self.display_board()
                self._display_game_over("score")
                game_running = False
            elif result == 'game_over_no_moves':
                 self.display_board()
                 self._display_game_over("no_moves")
                 game_running = False
            # 'placed', 'rerolled', 'invalid' -> continue loop

        print("\nExiting AI Assistance Mode.")


#----------------------------------------------------
# AI Play Alone Mode:

    def play_with_ai(self, algorithm_code, selected_heuristic_func, time_limit_per_move):
        """Allows the AI to play the game autonomously."""
        print(Fore.MAGENTA + "\n--- AI Playing Alone ---" + Style.RESET_ALL)
        print(f"Algorithm: {algorithm_code.upper()}")
        if selected_heuristic_func:
            print(f"Heuristic: {selected_heuristic_func.__name__}")
        print(f"Time Limit Per Move: {time_limit_per_move}s")
        print("-" * 30)

        move_count = 0
        consecutive_rerolls = 0
        start_time_game = time.time()

        game_running = True
        while game_running:
            self.display_board()
            self.display_piece()

            # Check game end conditions BEFORE AI makes a move
            if self.all_diamonds_collected:
                # Victory message printed by process_user_move if triggered there
                # If reached here directly, print it now.
                if not hasattr(self, '_victory_displayed'): # Avoid double printing
                     self._display_victory()
                     self._victory_displayed = True
                game_running = False
                continue
            if self.score <= 0:
                 if not hasattr(self, '_game_over_displayed'):
                      self._display_game_over("score")
                      self._game_over_displayed = True
                 game_running = False
                 continue
            if not self._has_valid_moves(self.current_piece):
                 print(f"{Fore.RED}AI has no valid moves for the current piece!{Style.RESET_ALL}")
                 # Attempt reroll if possible and within limits
                 reroll_cost = SCORE_PENALTY_REROLL_FACTOR * self.difficulty
                 if consecutive_rerolls < MAX_CONSECUTIVE_REROLLS and self.score > reroll_cost:
                     print(f"{Fore.YELLOW}Attempting reroll ({consecutive_rerolls + 1}/{MAX_CONSECUTIVE_REROLLS})...{Style.RESET_ALL}")
                     self.reroll()
                     consecutive_rerolls += 1
                     time.sleep(0.5) # Pause slightly after reroll
                     continue # Restart loop to check new piece/state
                 else:
                     if consecutive_rerolls >= MAX_CONSECUTIVE_REROLLS:
                          print(f"{Fore.RED}Max consecutive rerolls reached.{Style.RESET_ALL}")
                     elif self.score <= reroll_cost:
                          print(f"{Fore.RED}Cannot reroll (score {self.score} too low, costs {reroll_cost}).{Style.RESET_ALL}")
                     else:
                          print(f"{Fore.RED}Cannot reroll (unknown reason).{Style.RESET_ALL}")

                     if not hasattr(self, '_game_over_displayed'):
                          self._display_game_over("no_moves")
                          self._game_over_displayed = True
                     game_running = False
                     continue

            # Reset consecutive rerolls if AI has valid moves
            consecutive_rerolls = 0

            # Get AI move
            ai_move = get_ai_move(self, algorithm_code, time_limit_per_move, selected_heuristic_func)

            if ai_move:
                r, c = ai_move
                move_count += 1
                print(f"\n--- AI Move #{move_count} ---")
                print(f"Action: Place piece at ({r}, {c})")
                # Simulate placing the piece (process_user_move handles validation, score, lines, new piece)
                result = self.process_user_move(f"{r} {c}")

                if result == 'placed':
                     print("Placement successful.")
                     time.sleep(0.5) # Pause slightly to allow reading output
                elif result == 'invalid': # Should not happen if get_ai_move is correct
                     print(f"{Fore.RED}Error: AI suggested an invalid move ({r},{c}). Stopping.{Style.RESET_ALL}")
                     game_running = False
                # process_user_move handles victory/game_over checks internally now
                elif result in ['victory', 'game_over_score', 'game_over_no_moves']:
                     # Set flags to avoid double printing end messages if loop terminates here
                     if result == 'victory': self._victory_displayed = True
                     else: self._game_over_displayed = True
                     game_running = False # Game ended by the move

            else: # AI failed to find a move (even though _has_valid_moves was true initially?)
                print(f"{Fore.YELLOW}AI ({algorithm_code.upper()}) could not find a move this turn.{Style.RESET_ALL}")
                 # Attempt reroll (this path might be redundant due to the check at the start of the loop)
                reroll_cost = SCORE_PENALTY_REROLL_FACTOR * self.difficulty
                if consecutive_rerolls < MAX_CONSECUTIVE_REROLLS and self.score > reroll_cost:
                     print(f"{Fore.YELLOW}Attempting reroll ({consecutive_rerolls + 1}/{MAX_CONSECUTIVE_REROLLS})...{Style.RESET_ALL}")
                     self.reroll()
                     consecutive_rerolls += 1
                     time.sleep(0.5)
                     continue
                else:
                     print(f"{Fore.RED}AI failed to find a move and cannot reroll. Game over.{Style.RESET_ALL}")
                     if not hasattr(self, '_game_over_displayed'):
                          self._display_game_over("no_moves") # Or maybe score? Check score too.
                          self._game_over_displayed = True
                     game_running = False


        # --- AI Play Summary ---
        end_time_game = time.time()
        total_time = end_time_game - start_time_game
        print(Fore.MAGENTA + "\n--- AI Play Summary ---")
        print(f"Algorithm Used: {algorithm_code.upper()}")
        if selected_heuristic_func: print(f"Heuristic Used: {selected_heuristic_func.__name__}")
        print(f"Total Moves Made: {move_count}")
        print(f"Total Time: {total_time:.2f} seconds")
        # Final state is already displayed by victory/game over messages
        print("-----------------------" + Style.RESET_ALL)


#----------------------------------------------------
# Helper to select AI algorithm and heuristic:

    def _select_ai_algorithm_and_heuristic(self):
        """Prompts user to select AI algorithm and heuristic (if applicable)."""
        algorithms = {
            'uninformed': {
                '1': ('bfs', 'BFS (Breadth-First Search)'),
                '2': ('dfs', 'DFS (Depth-First Search)'),
                '3': ('ucs', 'UCS (Uniform Cost Search)'),
                '4': ('dls', 'DLS (Depth-Limited Search)'),
                '5': ('ids', 'IDS (Iterative Deepening Search)')
            },
            'informed': {
                '6': ('greedy', 'Greedy Search'),
                '7': ('astar', 'A* Search'),
                '8': ('wastar', 'Weighted A* Search')
            }
        }
        # Updated heuristics map
        heuristics_map = {
            '1': ('Diamond Proximity', heuristic_diamond_proximity),
            '2': ('Maximize Score (Lookahead)', heuristic_maximize_score) # Renamed reference
        }

        print("\n--- Select AI Algorithm ---")
        print("Uninformed:")
        for k, v in algorithms['uninformed'].items(): print(f"  {k} - {v[1]}")
        print("Informed (Require Heuristic):")
        for k, v in algorithms['informed'].items(): print(f"  {k} - {v[1]}")
        print("  Q - Cancel")

        while True:
            choice = input("Algorithm choice (1-8, Q): ").strip().lower()
            if choice == 'q': return None, None
            selected_algo_info = None
            if choice in algorithms['uninformed']:
                selected_algo_info = algorithms['uninformed'][choice]
                break
            elif choice in algorithms['informed']:
                selected_algo_info = algorithms['informed'][choice]
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1-8 or Q.{Style.RESET_ALL}")

        algorithm_code = selected_algo_info[0]
        selected_heuristic_func = None

        # Select heuristic if informed algorithm chosen
        if algorithm_code in [a[0] for a in algorithms['informed'].values()]:
            print("\n--- Select Heuristic ---")
            for k, v in heuristics_map.items(): print(f"  {k} - {v[0]}") # Use updated map
            print("  Q - Cancel")
            while True:
                # Adjust prompt for new number of heuristics
                h_choice = input(f"Heuristic choice for {algorithm_code.upper()} (1-{len(heuristics_map)}, Q): ").strip().lower()
                if h_choice == 'q': return None, None
                if h_choice in heuristics_map:
                    selected_heuristic_func = heuristics_map[h_choice][1]
                    print(f"Selected Heuristic: {heuristics_map[h_choice][0]}")
                    break
                else:
                     # Adjust error message for new number of heuristics
                     print(f"{Fore.RED}Invalid choice. Please enter 1-{len(heuristics_map)} or Q.{Style.RESET_ALL}")

        return algorithm_code, selected_heuristic_func

#----------------------------------------------------
# Mode for letting AI play alone:

    def _play_with_ai_mode(self):
        """Sets up and runs the AI playing alone mode."""
        algorithm_code, selected_heuristic_func = self._select_ai_algorithm_and_heuristic()
        if algorithm_code is None:
            print("AI Play setup cancelled.")
            return

        time_limit_move = AI_PLAY_TIME_LIMIT_BASE + (self.difficulty * AI_TIME_LIMIT_DIFFICULTY_MULTIPLIER)
        self.play_with_ai(algorithm_code, selected_heuristic_func, time_limit_move)
        input("\nPress Enter to return to the main menu...")


#-----------------------------------------------------
#Main Execution Block:

if __name__ == "__main__":
    running = True
    random.seed() # Seed random number generator

    while running:
        print(Fore.CYAN + "\n========================================")
        print("      Wood Block Puzzle AI Edition")
        print("    Developed by: Ricardo Gonçalves (rdtg94)")
        print("========================================" + Style.RESET_ALL)
        print("1 - Play Game (Human)")
        print("2 - Play with AI Assistance")
        print("3 - Let the AI Play Alone")
        print("Q - Exit Game")
        print("----------------------------------------")

        main_choice = input("Choose an option (1-3, Q): ").strip().lower()

        if main_choice == 'q':
            print("\nThank you for playing! Goodbye!")
            running = False
            continue

        if main_choice in ['1', '2', '3']:
            print("\n--- Select Difficulty ---")
            print("1 - Easy (4x4)")
            print("2 - Medium (5x5)")
            print("3 - Hard (6x6)")
            print("4 - Expert (7x7)")
            print("Q - Return to Main Menu")
            print("-------------------------")

            diff_choice = input("Enter difficulty (1-4, Q): ").strip().lower()

            if diff_choice == 'q':
                continue # Go back to main menu

            try:
                difficulty = int(diff_choice)
                if not 1 <= difficulty <= 4:
                    raise ValueError("Difficulty must be between 1 and 4.")
            except ValueError as e:
                print(f"{Fore.RED}Invalid difficulty input: {e}. Please try again.{Style.RESET_ALL}")
                continue

            # Create the game instance
            game = WoodBlockPuzzle(difficulty=difficulty)

            # Start the chosen game mode
            if main_choice == '1':
                game.play()
            elif main_choice == '2':
                game._provide_ai_suggestion()
            elif main_choice == '3':
                game._play_with_ai_mode()

        else:
            print(f"{Fore.RED}Invalid option '{main_choice}'. Please choose 1, 2, 3, or Q.{Style.RESET_ALL}")
