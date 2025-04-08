# Date: 2025-04-08
# Version: 3.0
# Author: Ricardo Gonçalves (rdtg94)
# Description: GUI version of Wood Block Puzzle

import pygame
import sys
import random
import math
import time
import pygame_gui # Still used for in-game/post-game buttons
import os # Potentially needed for robust path joining

# Import game logic and AI components
from constants import *
from game_state import GameState
from Ai_algorithms import heuristic_first_move
# Keep other imports if needed

# --- Pygame Setup ---
try:
    pygame.init()
    pygame.font.init() # Initialize font module early
except Exception as e:
    print(f"FATAL: Pygame initialization failed: {e}")
    sys.exit()

# --- Constants for GUI ---
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 700
GRID_LINE_WIDTH = 1
CELL_BORDER_RADIUS = 3

# Colors
COLOR_BACKGROUND = (230, 240, 245)
COLOR_GRID_LINES = (180, 160, 130)
# Ensure COLOR_BOARD_CELL_BROWN is defined in constants.py or here:
if 'COLOR_BOARD_CELL_BROWN' not in locals() and 'COLOR_BOARD_CELL_BROWN' not in globals():
     COLOR_BOARD_CELL_BROWN = (210, 180, 140) # Tan / Soft Brown Fallback
COLOR_EMPTY_CELL = COLOR_BOARD_CELL_BROWN
COLOR_OBSTACLE = (110, 110, 110)
COLOR_PLACED_PIECE_TINT = (210, 180, 140) # Fallback if texture fails
COLOR_GHOST_VALID = (0, 255, 0, 100)
COLOR_GHOST_INVALID = (255, 0, 0, 100)
COLOR_TEXT = (30, 30, 30)
COLOR_TEXT_DIAMOND = (60, 60, 60)
COLOR_AUTHOR = (100, 100, 100)
COLOR_MESSAGE_BG = (245, 245, 245) # Used? Maybe remove if not.
COLOR_HINT_BORDER = (255, 165, 0)

# Difficulty Button Colors
COLOR_DIFFICULTY_BUTTONS = {
    1: {'bg': (144, 238, 144), 'hover': (104, 255, 104), 'text': (20, 20, 20)}, # Easy - Green
    2: {'bg': (255, 255, 153), 'hover': (255, 255, 110), 'text': (40, 40, 30)}, # Medium - Yellow
    3: {'bg': (255, 178, 102), 'hover': (255, 165, 70), 'text': (50, 30, 10)}, # Hard - Orange
    4: {'bg': (255, 102, 102), 'hover': (255, 80, 80), 'text': (40, 10, 10)}   # Expert - Red
}
COLOR_BUTTON_BORDER = (50, 50, 50)
COLOR_QUIT_BUTTON_BG = (200, 200, 200)
COLOR_QUIT_BUTTON_HOVER = (180, 180, 180)
COLOR_QUIT_BUTTON_TEXT = (50, 50, 50)


# Fonts
try:
    FONT_UI_SIZE = 30
    FONT_AUTHOR_SIZE = 20
    FONT_MESSAGE_SIZE = 40
    FONT_MENU_TITLE_SIZE = 55
    FONT_MENU_BUTTON_SIZE = FONT_UI_SIZE

    FONT_UI = pygame.font.SysFont('Arial', FONT_UI_SIZE)
    FONT_AUTHOR = pygame.font.SysFont('Arial', FONT_AUTHOR_SIZE)
    FONT_MESSAGE = pygame.font.SysFont('Arial', FONT_MESSAGE_SIZE, bold=True)
    FONT_MENU_TITLE = pygame.font.SysFont('Arial', FONT_MENU_TITLE_SIZE, bold=True)
    FONT_MENU_BUTTON = pygame.font.SysFont('Arial', FONT_MENU_BUTTON_SIZE, bold=True)
except Exception as e:
    print(f"Warning: Could not load Arial font. Using pygame default. Error: {e}")
    FONT_UI = pygame.font.Font(None, FONT_UI_SIZE + 4)
    FONT_AUTHOR = pygame.font.Font(None, FONT_AUTHOR_SIZE + 4)
    FONT_MESSAGE = pygame.font.Font(None, FONT_MESSAGE_SIZE + 4)
    FONT_MENU_TITLE = pygame.font.Font(None, FONT_MENU_TITLE_SIZE + 6)
    FONT_MENU_BUTTON = pygame.font.Font(None, FONT_MENU_BUTTON_SIZE + 4)


# Asset Loading Function
def load_scaled_image(filename, size):
    """Loads an image, scales it, and handles errors."""
    try:
        # Consider using absolute paths for robustness if needed
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # full_path = os.path.join(script_dir, filename)
        # image = pygame.image.load(full_path).convert_alpha()
        image = pygame.image.load(filename).convert_alpha() # Assumes in same dir
        return pygame.transform.smoothscale(image, size)
    except Exception as e:
        print(f"ERROR loading/scaling image '{filename}': {e}. Using fallback.")
        fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
        fallback_surface.fill((255, 0, 255, 100)) # Magenta fallback
        pygame.draw.rect(fallback_surface, (0,0,0), fallback_surface.get_rect(), 1)
        return fallback_surface

# --- Main GUI Class ---
class WoodBlockPuzzleGUIEnhanced:
    def __init__(self):
        """Initializes the game window, UI manager, and game state."""
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Wood Block Puzzle AI - by Ricardo Gonçalves (rdtg94)")
            self.clock = pygame.time.Clock()

            # Initialize UI Manager without theme file
            self.ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

            # Game State Variables
            self.game_state = 'MAIN_MENU'
            self.difficulty = 1
            self.board_size = BOARD_SIZE_BASE + self.difficulty
            self.difficulty_names = ['Easy', 'Medium', 'Hard', 'Expert']

            # Game Logic Variables (initialized in start_new_game)
            self.board = None; self.score = 0; self.current_piece_shape = None;
            self.total_diamonds = 0; self.diamonds_collected = 0; self.all_diamonds_collected = False;
            self.game_over_reason = None; self.victory_state = False;

            # GUI/Interaction Variables (initialized in start_new_game)
            self.cell_size = 0; self.grid_width = 0; self.grid_height = 0;
            self.grid_offset_x = 0; self.grid_offset_y = 0; self.piece_area_x = 0;
            self.piece_area_y = 0; self.piece_area_width = 220; self.piece_area_height = 180;
            self.dragging_piece = False; self.drag_offset_x = 0; self.drag_offset_y = 0;
            self.current_piece_screen_pos = (0, 0); self.ghost_pos_grid = None;
            self.ghost_valid = False; self.ai_hint_move = None; self.ai_hint_timer = 0;
            self.AI_HINT_DURATION = 120 # 2 seconds at 60 FPS

            # Loaded Assets
            self.diamond_image = None
            self.wood_cell_image = None

            # UI Elements
            self.main_menu_elements = {} # Stores Rects for manual buttons
            self.game_ui_elements = {}   # Stores pygame_gui elements
            self.post_game_elements = {} # Stores pygame_gui elements

            self._setup_main_menu_ui() # Setup initial UI state

        except Exception as e:
            print(f"\nFATAL ERROR during GUI Initialization: {e}")
            import traceback; traceback.print_exc(); pygame.quit(); sys.exit()

    def start_new_game(self, difficulty):
        """Initializes or resets the game state for the chosen difficulty."""
        try:
            self.difficulty = difficulty
            self.board_size = BOARD_SIZE_BASE + self.difficulty
            self.difficulty_names = ['Easy', 'Medium', 'Hard', 'Expert']

            # Reset Game Logic Vars
            self.score = 100 * self.difficulty
            self.diamonds_collected = 0
            self.all_diamonds_collected = False
            self.game_over_reason = None
            self.victory_state = False

            self.board = self._create_initial_board()
            self.total_diamonds = self._count_diamonds()
            self.all_diamonds_collected = (self.total_diamonds == 0)

            self.current_piece_shape = GameState._generate_random_piece(self.difficulty)

            # Reset GUI/Interaction Vars
            max_grid_dim = 500
            self.cell_size = min(max_grid_dim // self.board_size, 90)
            self.grid_width = self.board_size * self.cell_size
            self.grid_height = self.board_size * self.cell_size
            self.grid_offset_x = 60
            self.grid_offset_y = 100
            self.piece_area_x = self.grid_offset_x + self.grid_width + 50
            self.piece_area_y = self.grid_offset_y
            self.piece_area_width = 220
            self.piece_area_height = 180

            self.dragging_piece = False
            self.ghost_pos_grid = None
            self.ai_hint_move = None
            self.ai_hint_timer = 0
            # Calculate initial piece position AFTER cell_size is known
            self.current_piece_screen_pos = self._get_initial_piece_screen_pos()

            # Load/Scale Assets
            self.diamond_image = load_scaled_image('diamond.png', (int(self.cell_size*0.8), int(self.cell_size*0.8)))
            self.wood_cell_image = load_scaled_image('wood_texture.png', (self.cell_size, self.cell_size))

            self._clear_all_ui_elements() # Clear menu elements
            self._setup_game_ui()         # Setup in-game UI
            self.game_state = 'PLAYING'
            pygame.display.set_caption(f"Wood Block Puzzle AI - {self.difficulty_names[self.difficulty-1]} - by Ricardo Gonçalves (rdtg94)")
        except Exception as e:
            print(f"\nFATAL ERROR during start_new_game(difficulty={difficulty}): {e}")
            import traceback; traceback.print_exc()
            # Attempt to recover to main menu
            self.game_state = 'MAIN_MENU'
            try: self._setup_main_menu_ui()
            except: pygame.quit(); sys.exit() # Exit if menu setup fails too

    # --- UI Element Management ---
    def _clear_all_ui_elements(self):
        """Kills all active pygame_gui elements and clears tracking dicts."""
        self.ui_manager.clear_and_reset()
        self.main_menu_elements.clear()
        self.game_ui_elements.clear()
        self.post_game_elements.clear()

    def _setup_main_menu_ui(self):
        """Sets up UI elements for the main menu (manual buttons)."""
        try:
            self._clear_all_ui_elements()
            title_y = SCREEN_HEIGHT * 0.15
            button_start_y = title_y + 100
            button_height = 55; button_width = 280; button_spacing = 25
            center_x = SCREEN_WIDTH // 2

            self.main_menu_elements['buttons'] = []
            difficulties = [(1, "Easy (4x4)"), (2, "Medium (5x5)"), (3, "Hard (6x6)"), (4, "Expert (7x7)")]
            for i, (diff_level, diff_text) in enumerate(difficulties):
                button_rect = pygame.Rect(0, 0, button_width, button_height)
                button_rect.center = (center_x, button_start_y + i * (button_height + button_spacing))
                self.main_menu_elements['buttons'].append({'rect': button_rect, 'level': diff_level, 'text': diff_text})

            quit_button_rect = pygame.Rect(0, 0, button_width // 1.5, button_height * 0.8)
            quit_button_rect.center = (center_x, button_start_y + len(difficulties) * (button_height + button_spacing) + 20)
            self.main_menu_elements['quit_rect'] = quit_button_rect
        except Exception as e: print(f"ERROR setting up Main Menu UI: {e}"); import traceback; traceback.print_exc()

    def _setup_game_ui(self):
        """Sets up UI elements for the main game screen (using pygame_gui)."""
        try:
            self._clear_all_ui_elements()
            button_width = 190; button_height = 50
            button_x = self.piece_area_x + (self.piece_area_width - button_width) // 2
            start_y = self.piece_area_y + self.piece_area_height + 100

            self.game_ui_elements['reroll'] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(button_x, start_y, button_width, button_height), text="Reroll", manager=self.ui_manager)
            hint_rect = pygame.Rect(button_x, self.game_ui_elements['reroll'].relative_rect.bottom + 15, button_width, button_height)
            self.game_ui_elements['ai_hint'] = pygame_gui.elements.UIButton(relative_rect=hint_rect, text="AI Hint (Instant)", manager=self.ui_manager)
            hint_label_rect = pygame.Rect(button_x, hint_rect.bottom + 5, button_width, 35)
            self.game_ui_elements['hint_label'] = pygame_gui.elements.UILabel(relative_rect=hint_label_rect, text="", manager=self.ui_manager)
            quit_rect = pygame.Rect(button_x, hint_rect.bottom + 45, button_width, button_height)
            self.game_ui_elements['quit'] = pygame_gui.elements.UIButton(relative_rect=quit_rect, text="Quit to Menu", manager=self.ui_manager)
        except Exception as e: print(f"ERROR setting up Game UI: {e}"); import traceback; traceback.print_exc()

    def _setup_post_game_ui(self, message, message_color=(255,255,255)):
        """Sets up UI elements for the post-game screen (using pygame_gui)."""
        try:
            self._clear_all_ui_elements()
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            msg_width, msg_height = 500, 100
            msg_rect = pygame.Rect(0, 0, msg_width, msg_height); msg_rect.center = (center_x, center_y - 60)
            self.post_game_elements['message'] = pygame_gui.elements.UILabel(relative_rect=msg_rect, text=message, manager=self.ui_manager)
            # Note: Setting color programmatically in pygame_gui without themes is tricky. Message color might be default.

            button_width, button_height = 220, 55
            button_y = center_y + 40
            play_again_rect = pygame.Rect(0, 0, button_width, button_height); play_again_rect.center = (center_x, button_y)
            self.post_game_elements['play_again'] = pygame_gui.elements.UIButton(relative_rect=play_again_rect, text="Play Again", manager=self.ui_manager)
            quit_rect = pygame.Rect(0, 0, button_width, button_height); quit_rect.center = (center_x, button_y + button_height + 20)
            self.post_game_elements['quit'] = pygame_gui.elements.UIButton(relative_rect=quit_rect, text="Quit Game", manager=self.ui_manager)
        except Exception as e: print(f"ERROR setting up Post Game UI: {e}"); import traceback; traceback.print_exc()

    # --- Game Logic Methods ---
    def _create_initial_board(self):
        """Creates the initial game board."""
        if not hasattr(self, 'board_size') or self.board_size <= 0: return [[]]
        board = [[" " for _ in range(self.board_size)] for _ in range(self.board_size)]
        total_cells = self.board_size * self.board_size
        num_diamonds = max(MIN_DIAMONDS, math.floor(DIAMOND_PERCENTAGE * total_cells))
        num_obstacles = max(MIN_OBSTACLES, math.floor(OBSTACLE_PERCENTAGE * total_cells))
        if num_diamonds + num_obstacles >= total_cells:
            num_obstacles = max(0, total_cells - num_diamonds - 1)
        all_coords = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
        random.shuffle(all_coords)
        coords_iterator = iter(all_coords)
        placed_count = 0
        try:
            while placed_count < num_diamonds: r, c = next(coords_iterator); board[r][c] = "D"; placed_count += 1
        except StopIteration: pass
        obstacles_placed = 0
        try:
            while obstacles_placed < num_obstacles:
                r, c = next(coords_iterator)
                if board[r][c] == " ": board[r][c] = "#"; obstacles_placed += 1
        except StopIteration: pass
        return board

    def _count_diamonds(self):
        """Counts diamonds on the current board."""
        return sum(row.count("D") for row in self.board) if self.board else 0

    def _get_initial_piece_screen_pos(self):
        """Calculates the screen position for the piece display area."""
        if not self.current_piece_shape or self.cell_size <= 0:
             return (self.piece_area_x + 20, self.piece_area_y + 20)
        piece_h = len(self.current_piece_shape); piece_w = len(self.current_piece_shape[0])
        px_w = piece_w * self.cell_size; px_h = piece_h * self.cell_size
        center_x = self.piece_area_x + self.piece_area_width // 2
        center_y = self.piece_area_y + self.piece_area_height // 2
        return (center_x - px_w // 2, center_y - px_h // 2)

    def _can_place_piece_at(self, piece_shape, r, c):
        """Checks if the piece can be placed at grid pos (r, c)."""
        if not piece_shape or not self.board: return False
        h, w = len(piece_shape), len(piece_shape[0])
        if r < 0 or c < 0 or r + h > self.board_size or c + w > self.board_size: return False
        for i in range(h):
            for j in range(w):
                if piece_shape[i][j] == 1:
                     if not (0 <= r + i < self.board_size and 0 <= c + j < self.board_size): return False # Redundant but safe
                     if self.board[r + i][c + j] != " ": return False
        return True

    def _has_valid_moves(self, piece_shape):
         """Checks if the piece has any valid placement."""
         if not piece_shape or not self.board: return False
         h, w = len(piece_shape), len(piece_shape[0])
         for r in range(self.board_size - h + 1):
             for c in range(self.board_size - w + 1):
                 if self._can_place_piece_at(piece_shape, r, c): return True
         return False

    def place_piece_on_board(self, piece_shape, r, c):
        """Places piece, updates score, checks lines, gets new piece, checks end game."""
        if not self._can_place_piece_at(piece_shape, r, c): return False
        h, w = len(piece_shape), len(piece_shape[0])
        for i in range(h):
            for j in range(w):
                if piece_shape[i][j] == 1: self.board[r + i][c + j] = "#"
        self.score -= SCORE_PENALTY_PLACE_PIECE
        self.check_full_lines_and_columns()
        self.current_piece_shape = GameState._generate_random_piece(self.difficulty)
        self.current_piece_screen_pos = self._get_initial_piece_screen_pos()
        self.check_game_end_conditions() # Check AFTER getting new piece
        return True

    def check_full_lines_and_columns(self):
        """Checks/clears lines/columns, updates score/diamonds."""
        if not self.board: return
        lines_to_clear, cols_to_clear, diamonds_captured = [], [], 0
        for r in range(self.board_size):
            if all(self.board[r][c] in ["#", "D"] for c in range(self.board_size)): lines_to_clear.append(r)
        for c in range(self.board_size):
            if all(self.board[r][c] in ["#", "D"] for r in range(self.board_size)): cols_to_clear.append(c)
        if not lines_to_clear and not cols_to_clear: return
        cleared = set()
        for r in lines_to_clear:
            for c in range(self.board_size):
                if (r, c) not in cleared:
                    if self.board[r][c] == "D": diamonds_captured += 1
                    self.board[r][c] = " "; cleared.add((r, c))
        for c in cols_to_clear:
            for r in range(self.board_size):
                if (r, c) not in cleared:
                    if self.board[r][c] == "D": diamonds_captured += 1
                    self.board[r][c] = " "; cleared.add((r, c))
        l_count, c_count = len(lines_to_clear), len(cols_to_clear)
        base_pts = SCORE_BASE_LINE_CLEAR * self.difficulty; diamond_b = SCORE_DIAMOND_BONUS * self.difficulty
        score_g = (l_count + c_count) * base_pts
        combo_b = max(0, (l_count + c_count - 1)) * base_pts // SCORE_COMBO_BONUS_DIVISOR
        diamond_pts = diamonds_captured * diamond_b
        self.score += score_g + combo_b + diamond_pts
        self.diamonds_collected += diamonds_captured
        # Victory check moved

    def attempt_reroll(self):
        """Handles the reroll action if possible."""
        if self.game_state != 'PLAYING': return
        penalty = SCORE_PENALTY_REROLL_FACTOR * self.difficulty
        if self.score >= penalty:
            self.score -= penalty
            self.current_piece_shape = GameState._generate_random_piece(self.difficulty)
            self.current_piece_screen_pos = self._get_initial_piece_screen_pos()
            self.check_game_end_conditions()
        else:
            print("Not enough points to reroll.") # TODO: Show in GUI?

    def check_game_end_conditions(self):
        """Checks for victory or game over and transitions state."""
        if self.game_state != 'PLAYING': return False

        # Victory Check
        if self.total_diamonds > 0 and self.diamonds_collected >= self.total_diamonds:
            self.victory_state = True; self.game_state = 'VICTORY'
            self._setup_post_game_ui("VICTORY!", (0, 180, 0))
            return True

        # Game Over Checks
        game_over = False; reason = None
        if self.score <= 0:
            reason = "score"; game_over = True
        elif not self._has_valid_moves(self.current_piece_shape):
             reason = "no_moves"; game_over = True

        if game_over:
            self.game_over_reason = reason; self.game_state = 'GAME_OVER'
            message = "GAME OVER - No Score!" if reason == "score" else "GAME OVER - No Moves!"
            self._setup_post_game_ui(message, (180, 0, 0))
            return True
        return False

    def request_ai_hint(self):
        """Gets an *instant* AI move suggestion (first valid move)."""
        if self.game_state != 'PLAYING': return
        current_game_state = GameState(
            board=self.board, current_piece=self.current_piece_shape, score=self.score,
            difficulty=self.difficulty, diamonds_collected=self.diamonds_collected,
            total_diamonds=self.total_diamonds
        )
        suggested_move = heuristic_first_move(current_game_state)
        hint_label = self.game_ui_elements.get('hint_label')
        if suggested_move:
            self.ai_hint_move = suggested_move
            self.ai_hint_timer = self.AI_HINT_DURATION
            if hint_label: hint_label.set_text(f"AI Suggests: {suggested_move}")
        else:
            self.ai_hint_move = None; self.ai_hint_timer = 0
            if hint_label: hint_label.set_text("AI: No moves found!")

    # --- Coordinate Conversion ---
    def _get_grid_pos_from_screen(self, screen_x, screen_y):
        """Converts screen coords to grid (row, col), returns None if outside."""
        if self.cell_size <= 0: return None
        if not (self.grid_offset_x <= screen_x < self.grid_offset_x + self.grid_width and
                self.grid_offset_y <= screen_y < self.grid_offset_y + self.grid_height):
            return None
        col = int((screen_x - self.grid_offset_x) // self.cell_size)
        row = int((screen_y - self.grid_offset_y) // self.cell_size)
        # Clamp values to be safe
        row = max(0, min(row, self.board_size - 1)); col = max(0, min(col, self.board_size - 1))
        return row, col

    def _get_screen_pos_from_grid(self, r, c):
        """Converts grid (row, col) to screen coords (top-left)."""
        x = self.grid_offset_x + c * self.cell_size
        y = self.grid_offset_y + r * self.cell_size
        return x, y

    # --- Event Handling ---
    def handle_events(self, time_delta):
        """Processes Pygame and Pygame GUI events based on game state."""
        if not hasattr(self, 'ui_manager'): return False # Safety check

        mouse_pos = pygame.mouse.get_pos() # Get mouse position once per frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("--- INFO: QUIT event received.")
                return False # Signal to quit the application

            # Process pygame_gui events first for its elements, EXCEPT in main menu
            process_gui_event = (self.game_state != 'MAIN_MENU')
            if process_gui_event:
                 try:
                      # Only process if manager exists
                      if hasattr(self, 'ui_manager') and self.ui_manager:
                           self.ui_manager.process_events(event)
                 except Exception as e:
                      print(f"--- ERROR processing GUI event: {e}")

            # --- State-Specific Event Handling ---

            # --- MAIN MENU --- (Manual Buttons)
            if self.game_state == 'MAIN_MENU':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left Click
                    clicked_on_button = False
                    for button_data in self.main_menu_elements.get('buttons', []):
                        if button_data['rect'].collidepoint(mouse_pos):
                            # print(f"--- DEBUG: Difficulty button {button_data['level']} clicked.") # Removed Debug
                            self.start_new_game(button_data['level'])
                            clicked_on_button = True
                            break # Exit loop once a button is clicked
                    if not clicked_on_button:
                        quit_rect = self.main_menu_elements.get('quit_rect')
                        if quit_rect and quit_rect.collidepoint(mouse_pos):
                             # print("--- DEBUG: Quit button clicked in menu.") # Removed Debug
                             return False # Quit application

            # --- PLAYING --- (Piece Dragging + pygame_gui Buttons)
            elif self.game_state == 'PLAYING':

                 # --- MOUSE BUTTON DOWN ---
                 if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     # print(f"--- DEBUG: MOUSEBUTTONDOWN at {mouse_pos} in PLAYING state") # Removed Debug

                     # Get piece rect for collision check
                     piece_rect = self._get_current_piece_rect()
                     # print(f"    Current Piece Screen Pos: {self.current_piece_screen_pos}") # Removed Debug
                     # print(f"    Calculated Piece Rect: {piece_rect}") # Removed Debug

                     if piece_rect and piece_rect.collidepoint(mouse_pos):
                         # Check if this click was also over a known GUI button rect as a safeguard
                         is_over_known_gui_button = False
                         if hasattr(self, 'ui_manager') and self.ui_manager:
                             for element in self.game_ui_elements.values():
                                 # Check if element exists, has a rect, and mouse collides
                                 if element and hasattr(element, 'rect') and element.rect.collidepoint(mouse_pos):
                                     is_over_known_gui_button = True
                                     # print(f"--- DEBUG: Click on piece rect, but also on GUI element rect: {element}") # Removed Debug
                                     break # Found collision with GUI button

                         # Start drag only if click was on piece AND not on a known GUI button rect
                         if not is_over_known_gui_button:
                             # print("--- DEBUG: Clicked on piece! Starting drag.") # Removed Debug
                             self.dragging_piece = True
                             self.drag_offset_x = mouse_pos[0] - piece_rect.x
                             self.drag_offset_y = mouse_pos[1] - piece_rect.y
                             # print(f"--- DEBUG: Drag offset: ({self.drag_offset_x}, {self.drag_offset_y})") # Removed Debug
                             self.ai_hint_move = None; self.ai_hint_timer = 0
                             if self.game_ui_elements.get('hint_label'): self.game_ui_elements['hint_label'].set_text("")
                         # else: # Click was on piece but also on GUI button
                         #    print("--- DEBUG: Click on piece rect, but also over a known GUI button rect. Ignoring drag.") # Removed Debug

                     # else: # Click was not on piece rect
                     #    print("--- DEBUG: Click was not on piece rect (or rect was None).") # Removed Debug


                 # --- MOUSE BUTTON UP ---
                 elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                     if self.dragging_piece:
                         # print(f"--- DEBUG: MOUSEBUTTONUP while dragging at {mouse_pos}") # Removed Debug
                         self.dragging_piece = False
                         if self.ghost_pos_grid and self.ghost_valid:
                             r, c = self.ghost_pos_grid
                             # print(f"--- DEBUG: Attempting placement at {r, c}") # Removed Debug
                             placed_ok = self.place_piece_on_board(self.current_piece_shape, r, c)
                             if not placed_ok:
                                 # print("--- DEBUG: Placement failed post-drop. Snapping back.") # Removed Debug
                                 self.current_piece_screen_pos = self._get_initial_piece_screen_pos()
                         else:
                             # print("--- DEBUG: Invalid drop or no ghost, snapping back.") # Removed Debug
                             self.current_piece_screen_pos = self._get_initial_piece_screen_pos()
                         self.ghost_pos_grid = None


                 # --- MOUSE MOTION ---
                 elif event.type == pygame.MOUSEMOTION:
                     if self.dragging_piece:
                         self.current_piece_screen_pos = (mouse_pos[0] - self.drag_offset_x, mouse_pos[1] - self.drag_offset_y)
                         center_offset_x = self.cell_size // 2; center_offset_y = self.cell_size // 2
                         grid_pos = self._get_grid_pos_from_screen(self.current_piece_screen_pos[0] + center_offset_x, self.current_piece_screen_pos[1] + center_offset_y)
                         new_ghost_pos = None; new_ghost_valid = False
                         if grid_pos is not None:
                             grid_r, grid_c = grid_pos; new_ghost_pos = (grid_r, grid_c)
                             new_ghost_valid = self._can_place_piece_at(self.current_piece_shape, grid_r, grid_c)
                         if self.ghost_pos_grid != new_ghost_pos or self.ghost_valid != new_ghost_valid:
                             self.ghost_pos_grid = new_ghost_pos; self.ghost_valid = new_ghost_valid


                 # --- PYGAME_GUI BUTTON PRESSED ---
                 elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                     element = event.ui_element
                     # print(f"--- DEBUG: pygame_gui button pressed: {element}") # Removed Debug
                     if element == self.game_ui_elements.get('reroll'): self.attempt_reroll()
                     elif element == self.game_ui_elements.get('ai_hint'): self.request_ai_hint()
                     elif element == self.game_ui_elements.get('quit'): self.game_state = 'MAIN_MENU'; self._setup_main_menu_ui()


            # --- GAME_OVER / VICTORY --- (pygame_gui Buttons)
            elif self.game_state in ['GAME_OVER', 'VICTORY']:
                 if event.type == pygame_gui.UI_BUTTON_PRESSED:
                     element = event.ui_element
                     # print(f"--- DEBUG: pygame_gui post-game button pressed: {element}") # Removed Debug
                     if element == self.post_game_elements.get('play_again'): self.game_state = 'MAIN_MENU'; self._setup_main_menu_ui()
                     elif element == self.post_game_elements.get('quit'): return False

        return True # Keep running unless explicitly told to quit

    # --- Update Logic ---
    def update(self, time_delta):
        """Updates game state and UI manager."""
        if not hasattr(self, 'ui_manager'): return
        if self.game_state != 'MAIN_MENU':
            try: self.ui_manager.update(time_delta)
            except Exception as e: print(f"ERROR during ui_manager.update: {e}")

        if self.game_state == 'PLAYING':
            if self.ai_hint_timer > 0:
                self.ai_hint_timer -= 1
                if self.ai_hint_timer <= 0:
                    self.ai_hint_move = None
                    if self.game_ui_elements.get('hint_label'):
                         try: self.game_ui_elements['hint_label'].set_text("")
                         except: pass

    # --- Drawing Methods ---
    def draw_main_menu(self):
        """Draws the main menu with manual buttons."""
        try:
            title_surf = FONT_MENU_TITLE.render("Wood Block Puzzle AI", True, COLOR_TEXT)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.15))
            self.screen.blit(title_surf, title_rect)
            author_surf = FONT_AUTHOR.render("by Ricardo Gonçalves (rdtg94)", True, COLOR_AUTHOR)
            author_rect = author_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.15 + 90))
            self.screen.blit(author_surf, author_rect)
            mouse_pos = pygame.mouse.get_pos()
            for button_data in self.main_menu_elements.get('buttons', []):
                rect = button_data['rect']; level = button_data['level']; text = button_data['text']
                colors = COLOR_DIFFICULTY_BUTTONS.get(level, {'bg': (150,150,150), 'hover': (170,170,170), 'text': (0,0,0)})
                is_hovered = rect.collidepoint(mouse_pos); bg_color = colors['hover'] if is_hovered else colors['bg']
                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, COLOR_BUTTON_BORDER, rect, 2, border_radius=8)
                text_surf = FONT_MENU_BUTTON.render(text, True, colors['text'])
                text_rect = text_surf.get_rect(center=rect.center); self.screen.blit(text_surf, text_rect)
            quit_rect = self.main_menu_elements.get('quit_rect')
            if quit_rect:
                 is_hovered = quit_rect.collidepoint(mouse_pos); bg_color = COLOR_QUIT_BUTTON_HOVER if is_hovered else COLOR_QUIT_BUTTON_BG
                 pygame.draw.rect(self.screen, bg_color, quit_rect, border_radius=6)
                 pygame.draw.rect(self.screen, COLOR_BUTTON_BORDER, quit_rect, 1, border_radius=6)
                 quit_font = FONT_UI; text_surf = quit_font.render("Quit", True, COLOR_QUIT_BUTTON_TEXT)
                 text_rect = text_surf.get_rect(center=quit_rect.center); self.screen.blit(text_surf, text_rect)
        except Exception as e: print(f"ERROR during draw_main_menu: {e}"); import traceback; traceback.print_exc()

    def draw_board(self):
        """Draws the game board grid and its contents."""
        if not self.board or self.cell_size <= 0: return
        try:
            for r in range(self.board_size):
                for c in range(self.board_size):
                    cell_rect = pygame.Rect(self.grid_offset_x + c * self.cell_size, self.grid_offset_y + r * self.cell_size, self.cell_size, self.cell_size)
                    cell_content = self.board[r][c]
                    pygame.draw.rect(self.screen, COLOR_EMPTY_CELL, cell_rect, border_radius=CELL_BORDER_RADIUS)
                    if cell_content == "#":
                        if self.wood_cell_image: self.screen.blit(self.wood_cell_image, cell_rect.topleft)
                        else: pygame.draw.rect(self.screen, COLOR_PLACED_PIECE_TINT[:3], cell_rect, border_radius=CELL_BORDER_RADIUS)
                    elif cell_content == "D":
                        if self.diamond_image: img_rect = self.diamond_image.get_rect(center=cell_rect.center); self.screen.blit(self.diamond_image, img_rect)
                        else: pygame.draw.circle(self.screen, (255, 255, 255), cell_rect.center, int(self.cell_size * 0.35)); pygame.draw.circle(self.screen, COLOR_TEXT, cell_rect.center, int(self.cell_size * 0.35), 1)
                    pygame.draw.rect(self.screen, COLOR_GRID_LINES, cell_rect, GRID_LINE_WIDTH, border_radius=CELL_BORDER_RADIUS)
            if self.ai_hint_move and self.ai_hint_timer > 0:
                 r_hint, c_hint = self.ai_hint_move
                 if self.current_piece_shape:
                      h, w = len(self.current_piece_shape), len(self.current_piece_shape[0])
                      for i in range(h):
                           for j in range(w):
                                if self.current_piece_shape[i][j] == 1:
                                     hr, hc = r_hint + i, c_hint + j
                                     if 0 <= hr < self.board_size and 0 <= hc < self.board_size:
                                          h_rect = pygame.Rect(self.grid_offset_x + hc * self.cell_size, self.grid_offset_y + hr * self.cell_size, self.cell_size, self.cell_size)
                                          pygame.draw.rect(self.screen, COLOR_HINT_BORDER, h_rect, 3, border_radius=CELL_BORDER_RADIUS)
        except Exception as e: print(f"ERROR during draw_board: {e}"); import traceback; traceback.print_exc()

    def draw_piece(self, piece_shape, screen_x, screen_y, alpha=255):
        """Draws a piece shape using wood texture."""
        if not piece_shape or self.cell_size <= 0: return
        try:
            texture = self.wood_cell_image
            fallback_color = COLOR_PLACED_PIECE_TINT[:3]
            for r, row in enumerate(piece_shape):
                for c, cell in enumerate(row):
                    if cell == 1:
                        cell_rect = pygame.Rect(screen_x + c * self.cell_size, screen_y + r * self.cell_size, self.cell_size, self.cell_size)
                        if texture:
                            if alpha < 255: temp = texture.copy(); temp.set_alpha(alpha); self.screen.blit(temp, cell_rect.topleft)
                            else: self.screen.blit(texture, cell_rect.topleft)
                        else:
                            if alpha < 255: s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA); s.fill(fallback_color + (alpha,)); self.screen.blit(s, cell_rect.topleft)
                            else: pygame.draw.rect(self.screen, fallback_color, cell_rect, border_radius=CELL_BORDER_RADIUS)
                        pygame.draw.rect(self.screen, tuple(max(0, x-50) for x in fallback_color), cell_rect, 1, border_radius=CELL_BORDER_RADIUS)
        except Exception as e: print(f"ERROR during draw_piece: {e}"); import traceback; traceback.print_exc()

    def _get_current_piece_rect(self):
         """Calculates the bounding rect for the current piece."""
         if not self.current_piece_shape or self.cell_size <= 0 : return None
         h = len(self.current_piece_shape); w = len(self.current_piece_shape[0])
         return pygame.Rect(self.current_piece_screen_pos[0], self.current_piece_screen_pos[1], w * self.cell_size, h * self.cell_size)

    def draw_ghost_piece(self):
        """Draws the semi-transparent preview of the piece on the grid."""
        if self.dragging_piece and self.ghost_pos_grid and self.current_piece_shape and self.cell_size > 0:
            try:
                r, c = self.ghost_pos_grid; screen_x, screen_y = self._get_screen_pos_from_grid(r, c)
                color = COLOR_GHOST_VALID[:3] if self.ghost_valid else COLOR_GHOST_INVALID[:3]; alpha = COLOR_GHOST_VALID[3]
                for i, row in enumerate(self.current_piece_shape):
                     for j, cell in enumerate(row):
                          if cell == 1:
                               s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA); s.fill(color + (alpha,)); self.screen.blit(s, (screen_x + j*self.cell_size, screen_y + i*self.cell_size))
                               pygame.draw.rect(self.screen, color, (screen_x + j*self.cell_size, screen_y + i*self.cell_size, self.cell_size, self.cell_size), 1, border_radius=CELL_BORDER_RADIUS)
            except Exception as e: print(f"ERROR during draw_ghost_piece: {e}"); import traceback; traceback.print_exc()

    def draw_static_ui_text(self):
        """Draws text elements not handled by pygame_gui manager."""
        try:
            score_surf = FONT_UI.render(f"Score: {self.score}", True, COLOR_TEXT); self.screen.blit(score_surf, (self.piece_area_x, self.piece_area_y + self.piece_area_height + 20))
            diamonds_surf = FONT_UI.render(f"Diamonds: {self.diamonds_collected} / {self.total_diamonds}", True, COLOR_TEXT_DIAMOND); self.screen.blit(diamonds_surf, (self.piece_area_x, self.piece_area_y + self.piece_area_height + 60))
            author_surf = FONT_AUTHOR.render("Ricardo Gonçalves (rdtg94)", True, COLOR_AUTHOR); self.screen.blit(author_surf, (15, SCREEN_HEIGHT - 30))
        except Exception as e: print(f"ERROR during draw_static_ui_text: {e}"); import traceback; traceback.print_exc()

    def draw(self, time_delta):
        """Draws the entire game screen based on the current state."""
        try:
            self.screen.fill(COLOR_BACKGROUND)

            if self.game_state == 'MAIN_MENU':
                self.draw_main_menu() # Draw manual menu elements

            elif self.game_state == 'PLAYING':
                self.draw_board()
                self.draw_static_ui_text() # Score, Diamonds, Author drawn manually
                if self.current_piece_shape: # Draw current piece only if it exists
                     self.draw_piece(self.current_piece_shape, self.current_piece_screen_pos[0], self.current_piece_screen_pos[1])
                self.draw_ghost_piece()
                if hasattr(self, 'ui_manager'): self.ui_manager.draw_ui(self.screen) # Draw pygame_gui elements

            elif self.game_state in ['GAME_OVER', 'VICTORY']:
                 self.draw_board() # Draw final board state
                 self.draw_static_ui_text()
                 overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((100, 100, 100, 170)); self.screen.blit(overlay, (0, 0))
                 if hasattr(self, 'ui_manager'): self.ui_manager.draw_ui(self.screen) # Draw pygame_gui elements

            pygame.display.flip()
        except Exception as e: print(f"ERROR during draw: {e}"); import traceback; traceback.print_exc()


    # --- Main Game Loop ---
    def run(self):
        """Runs the main application loop with error catching."""
        running = True
        print("--- INFO: Entering main loop ---")
        while running:
            try:
                time_delta = self.clock.tick(60) / 1000.0 # Time since last frame in seconds

                # Process events FIRST
                running = self.handle_events(time_delta)
                if not running: break

                # Update game state and UI manager
                self.update(time_delta)

                # Draw everything
                self.draw(time_delta)

            except Exception as e:
                print("\n--- UNCAUGHT FATAL ERROR in main loop ---")
                import traceback; traceback.print_exc()
                running = False # Exit loop on major error

        print("--- INFO: Exiting game loop. Quitting Pygame. ---")
        pygame.quit()


# --- Main Execution ---
if __name__ == "__main__":
    print("--- INFO: Starting application ---")
    # Ensure constant exists or define fallback
    if 'COLOR_BOARD_CELL_BROWN' not in locals() and 'COLOR_BOARD_CELL_BROWN' not in globals():
        COLOR_BOARD_CELL_BROWN = (210, 180, 140)
        print("--- WARNING: COLOR_BOARD_CELL_BROWN not found in constants, using default.")

    # Create and run the application
    try:
        game_app = WoodBlockPuzzleGUIEnhanced()
        game_app.run()
    except Exception as e:
         print(f"\n--- FATAL ERROR during application creation or run: {e}")
         import traceback; traceback.print_exc()
         pygame.quit() # Attempt to quit pygame if it was initialized

    print("--- INFO: Application finished ---")
    sys.exit() # Ensure script terminates cleanly
