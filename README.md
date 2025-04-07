# Wood Block Puzzle Game

## Introduction

Wood Block Puzzle is a challenging puzzle game where players strategically place blocks on a board to complete rows and columns. The game features multiple difficulty levels, various board sizes, and special game elements like diamonds for bonus points. It also includes an extensive AI system with multiple algorithms to assist gameplay or play automatically.

# Wood Block Puzzle Game

## Features

- **Multiple difficulty levels**: Easy, Medium, Hard, and Expert
- **Variable board sizes**: 4×4, 5×5, 6×6, and 7×7
- **Dynamic piece generation**: Different piece shapes based on the selected difficulty
- **Special game elements**: Diamonds for bonus points
- **Multiple gameplay modes**:
  - Human player mode
  - AI assistance mode
  - AI automatic play mode
- **Advanced AI algorithms**:
  - Uninformed search algorithms (BFS, DFS, UCS, DLS, IDS)
  - Informed search algorithms with heuristics (Greedy, A*, Weighted A*)

## How to Play

### Game Objective

- Complete rows and columns to clear them from the board
- Collect diamonds to gain bonus points
- Keep your score above zero to continue playing
- Collect all diamonds on the board to win

### Controls

- Enter coordinates (row column) to place the current piece on the board
- Enter 'R' to reroll and get a new piece (costs points)
- Enter 'Q' to quit the current game

### Scoring System

- Clearing rows and columns: 50 × difficulty points per row/column
- Combo bonus: Additional points for clearing multiple rows/columns at once
- Diamond collection: 100 × difficulty points per diamond
- Piece placement: -10 × (difficulty / 2) points penalty
- Rerolling pieces: -10 × (difficulty / 2) points penalty

## Game Mechanics

### Board Generation

The game generates a board with:
- Size determined by the difficulty level (Easy: 4×4, Medium: 5×5, Hard: 6×6, Expert: 7×7)
- Random placement of diamonds (approximately 10% of the board)
- Random placement of obstacles (approximately 10% of the board)

### Piece Generation

Pieces vary by difficulty:
- **Easy (Level 1)**: Basic shapes (straight lines and simple L shapes)
- **Medium (Level 2)**: Adds 2×2 squares and more complex L shapes
- **Hard (Level 3)**: Adds longer L shapes and more complex pieces
- **Expert (Level 4)**: Adds T shapes, Z shapes, and other complex configurations

### Line Clearing

When a row or column is completely filled with blocks or diamonds:
- The entire row/column is cleared
- Points are awarded based on the number of rows/columns cleared
- Diamonds in cleared rows/columns are collected and award bonus points
- Combo bonuses are awarded for clearing multiple rows/columns at once

## AI System

### Gameplay Modes with AI

1. **AI Assistance Mode**: The AI suggests the optimal move, and the player decides whether to follow the suggestion or make their own move.
2. **AI Automatic Play Mode**: The AI plays the game automatically using the selected algorithm and heuristic.

### Available AI Algorithms

#### Uninformed Search Algorithms

- **Breadth-First Search (BFS)**: Explores all possible moves level by level, guaranteeing the shortest solution path in terms of number of moves.
- **Depth-First Search (DFS)**: Explores as deep as possible along each branch before backtracking.
- **Uniform Cost Search (UCS)**: Prioritizes paths with the lowest cumulative cost.
- **Depth-Limited Search (DLS)**: Limits the depth of exploration to avoid going too deep.
- **Iterative Deepening Search (IDS)**: Combines the advantages of BFS and DFS by gradually increasing the depth limit.

#### Informed Search Algorithms

- **Greedy Search**: Uses a heuristic to estimate how close a state is to the goal without considering the path cost.
- **A-Star Search**: Combines the path cost and a heuristic to find the optimal solution.
- **Weighted A-Star Search**: Similar to A* but applies a weight to the heuristic, potentially finding solutions faster at the cost of optimality.

### Heuristics

- **Maximize Score**: Prioritizes moves that result in the highest immediate score gain.
- **Diamond Proximity**: Prioritizes moves that place pieces closer to diamonds on the board.

## Installation and Requirements


### Requirements

- Python 3.6 or higher
- Colorama package (for colored terminal output)

### Running the Game

Since the game is already installed on your computer, simply run:
```
python WoodPuzzle_Main.py
```

If the colorama package is not installed, you can install it with:
```
pip install colorama
```

## Project Structure

- `WoodPuzzle_Main.py`: Main game file with the core functionality and game loop
- `game_state.py`: Implementation of the GameState class for representing game states
- `Ai_algorithms.py`: Implementation of AI options for the game
- Search algorithm implementations:
  - `BFS.py`: Breadth-First Search algorithm
  - `DFS.py`: Depth-First Search algorithm
  - `UCS.py`: Uniform Cost Search algorithm
  - `DLS.py`: Depth-Limited Search algorithm
  - `IDS.py`: Iterative Deepening Search algorithm
  - `GREEDY.py`: Greedy Search algorithm
  - `A_STAR.py`: A* Search algorithm
  - `A_STAR_W.py`: Weighted A* Search algorithm

## Educational Value

This project serves as an excellent resource for learning about:
- Game design and mechanics
- Search algorithms in artificial intelligence
- Heuristic functions and their applications
- Game state representation and management
- Python programming and object-oriented design

## Credits

- **Authors**: Ricardo Gonçalves
- **Version**: 1.0
- **Date**: April 2025

