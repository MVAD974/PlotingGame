# -*- coding: utf-8 -*-
# @Author  : marc
# @Time    : 24/11/2025 17:01
# @File    : plotting_game.py
# @Project : Tests

"""
PlotingGame - Enhanced Version

This is the main entry point for the game. The code has been refactored into
multiple modules for better organization and maintainability:

- config.py: Configuration, constants, and colors
- simulation.py: Game logic and function evaluation
- renderer.py: All drawing and rendering code
- props.py: Drawing functions for objects and scenery
- characters.py: Character drawing functions
- game.py: Main game loop

This file now serves as a compatibility wrapper that imports and runs the
refactored game code.

Improvements in this version:
1. More complex functions (sinh, cosh, tanh, asin, acos, atan, floor, ceil)
2. Difficulty progression system (easy → medium → hard → expert)
3. Score and level tracking
4. Hint system (press 'H' for hints)
5. Enhanced scenery (plants, coffee machine, clock, particles)
6. Better code organization and modularity
7. Type hints for better code clarity

Controls:
- Type mathematical expressions to match the target function
- ENTER: Validate and go to next level when matched
- TAB: Skip current level (with score penalty)
- H: Get a hint (limited hints available)
- BACKSPACE: Edit your input
"""

# Import the game from the modular structure
from game import Game


# --- Backward Compatibility ---
# For anyone who imported these from the original file, we re-export them

from config import (
    WIDTH, HEIGHT, FPS, H_SPLIT,
    WINDOW_RECT_COORDS as WINDOW_RECT,
    FLOOR_Y, DESK_X, DESK_Y, DESK_WIDTH,
    COLORS as C,
    ALLOWED_MATH,
)
from simulation import Simulation
from renderer import Renderer


if __name__ == '__main__':
    Game().run()


# Import the game from the modular structure
from game import Game


# --- Backward Compatibility ---
# For anyone who imported these from the original file, we re-export them

from config import (
    WIDTH, HEIGHT, FPS, H_SPLIT,
    WINDOW_RECT_COORDS as WINDOW_RECT,
    FLOOR_Y, DESK_X, DESK_Y, DESK_WIDTH,
    COLORS as C,
    ALLOWED_MATH,
)
from simulation import Simulation
from renderer import Renderer


if __name__ == '__main__':
    Game().run()



if __name__ == '__main__':
    Game().run()