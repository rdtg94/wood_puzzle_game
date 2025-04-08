# Date: 2025-04-07
# Version: 1.0
# Author: Ricardo Gonçalves (rdtg94)
# Description: Defines constants used throughout the Wood Block Puzzle game.

# --- Scoring ---
SCORE_PENALTY_PLACE_PIECE = 10 # Base penalty for placing a piece
SCORE_PENALTY_REROLL_FACTOR = 10 # Multiplied by difficulty for reroll cost
SCORE_BASE_LINE_CLEAR = 50     # Multiplied by difficulty
SCORE_DIAMOND_BONUS = 100      # Multiplied by difficulty
SCORE_COMBO_BONUS_DIVISOR = 2  # For calculating combo bonus (base_points // divisor)

# --- AI Settings ---
DEFAULT_AI_TIME_LIMIT = 10      # Default time limit for AI move calculation (seconds)
DEFAULT_DLS_DEPTH_LIMIT = 10    # Default depth limit for DLS
DEFAULT_IDS_MAX_DEPTH = 50      # Default max depth to iterate up to in IDS
DEFAULT_WASTAR_WEIGHT = 1.5     # Default weight for Weighted A* heuristic
AI_SUGGESTION_TIME_LIMIT_BASE = 5 # Base time limit for AI suggestion mode
AI_PLAY_TIME_LIMIT_BASE = 5     # Base time limit per move for AI play alone mode
AI_TIME_LIMIT_DIFFICULTY_MULTIPLIER = 2 # Added time per difficulty level

# --- Game Mechanics ---
DIAMOND_PERCENTAGE = 0.10       # Percentage of board cells to be diamonds
OBSTACLE_PERCENTAGE = 0.10      # Percentage of board cells to be obstacles
MIN_DIAMONDS = 1                # Minimum number of diamonds
MIN_OBSTACLES = 1               # Minimum number of obstacles
MAX_CONSECUTIVE_REROLLS = 5     # Max times AI can reroll consecutively if stuck

# --- Board Size ---
BOARD_SIZE_BASE = 3             # Base size added to difficulty (e.g., diff 1 -> 3+1=4)

# --- Piece Generation Difficulty Thresholds ---
DIFFICULTY_MEDIUM_PIECES = 2
DIFFICULTY_HARD_PIECES = 3
DIFFICULTY_EXPERT_PIECES = 4

# --- Heuristic Default Values ---
HEURISTIC_DIAMOND_PROXIMITY_NO_DIAMOND_VALUE = 100 # Value if no diamonds exist

# --- Move Costs (for search algorithms like UCS, A*) ---
DEFAULT_MOVE_COST = 1

# --- GUI Colors ---
COLOR_DIFFICULTY_EASY = (144, 238, 144)  # Light Green
COLOR_DIFFICULTY_MEDIUM = (255, 255, 153) # Light Yellow
COLOR_DIFFICULTY_HARD = (255, 178, 102)  # Light Orange
COLOR_DIFFICULTY_EXPERT = (255, 102, 102)  # Light Red
COLOR_DIFFICULTY_TEXT = (30, 30, 30)      # Dark text for contrast
COLOR_BOARD_CELL_BROWN = (210, 180, 140) # Tan / Soft Brown
