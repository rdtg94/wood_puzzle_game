# Wood Block Puzzle Game

## Overview
Wood Block Puzzle is a strategic puzzle game where players place wooden blocks on a grid to clear lines and collect diamonds. The game includes intelligent hint systems and algorithmic solvers to assist players when they get stuck.

Author: Ricardo Gonçalves (rdtg94)
Version: 3.0 (April 2025)

## Game Objective
- Place wooden blocks on the game board
- Clear full lines and columns to earn points
- Collect diamonds for bonus points
- Progress through increasingly difficult levels
- Achieve the highest score possible before running out of valid moves

## Features
- Multiple difficulty levels with different board sizes
- Dynamic scoring system
- Diamond collection mechanic
- Wood-themed visual design
- Intelligent hint system
- Various search algorithms for move suggestions

## How to Play
1. **Start a Game**: Select a difficulty level from the main menu
2. **Place Blocks**: Drag and drop the current block onto the game board
3. **Clear Lines**: Fill an entire row or column to clear it and earn points
4. **Collect Diamonds**: Clear lines containing diamonds for bonus points
5. **Reroll Pieces**: Spend points to get a new piece if you're stuck (costs increase with difficulty)
6. **Use Hints**: Request a suggested move with the "AI Hint" button

### Controls
- **Left Mouse Button**: Click and drag to move blocks
- **Reroll Button**: Get a new random piece (costs points)
- **AI Hint Button**: Shows a suggested valid move
- **Quit Button**: Return to the main menu

### Game Mechanics
- **Scoring**:
  - Base penalty for placing a piece: 10 points
  - Base score for clearing a line: 50 points × difficulty
  - Diamond bonus: 100 points × difficulty
  - Combo bonus for multiple lines: (base_points ÷ 2) per additional line
  - Reroll penalty: 10 points × difficulty

- **Victory Condition**:
  - Collect all diamonds on the board

- **Game Over Conditions**:
  - Score drops to zero or below
  - No valid moves left for the current piece

## Difficulty Levels
1. **Easy**: 4×4 grid
2. **Medium**: 5×5 grid
3. **Hard**: 6×6 grid
4. **Expert**: 7×7 grid

Higher difficulties feature:
- Larger game boards
- More complex pieces
- Increased obstacle density
- Higher scoring potential

## Algorithms
The game implements multiple search algorithms for finding optimal moves:
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)
- Depth-Limited Search (DLS)
- Iterative Deepening Search (IDS)
- Greedy Best-First Search
- A* Search
- Weighted A* Search

## Requirements
- Python 3.6+
- Pygame
- Pygame_gui

## Installation

### Install Python Dependencies
```bash
pip install pygame pygame_gui
```

### Download Game Files
Clone the repository or download the game files:
```bash
git clone https://github.com/username/wood-block-puzzle.git
cd wood-block-puzzle
```

## Running the Game
Execute the main game file:
```bash
python WoodPuzzle_GUI.py
```

### Shell Version
The game also includes a console-based version for those who prefer to play in a terminal environment:
```bash
python WoodPuzzle_Shell.py
```
The shell version provides the same gameplay mechanics but with a text-based interface, making it suitable for environments where graphical display is unavailable or for users who prefer command-line interfaces.

## File Structure
- **WoodPuzzle_GUI.py**: Main game file with GUI implementation
- **constants.py**: Game constants and configuration values
- **game_state.py**: Game state representation and logic
- **Ai_algorithms.py**: Implementation of hint system and search algorithms
- **A_STAR.py**, **A_STAR_W.py**, **BFS.py**, etc.: Individual search algorithm implementations
- **diamond.png**, **wood_texture.png**: Game assets

## Troubleshooting
- **Missing Assets**: Ensure image files are in the same directory as the game
- **Display Issues**: Try adjusting screen resolution or window size
- **Performance Problems**: Lower difficulty levels require fewer computational resources
