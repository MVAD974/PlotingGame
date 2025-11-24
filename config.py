# -*- coding: utf-8 -*-
"""
Configuration and constants for PlotingGame.
Contains all game settings, colors, layout constants, and allowed math functions.
"""

import math
from enum import Enum
from typing import Final

# --- Window Configuration ---
WIDTH: Final[int] = 900
HEIGHT: Final[int] = 700
FPS: Final[int] = 60
H_SPLIT: Final[int] = 400  # Vertical split between lab (top) and terminal (bottom)


# --- Game States ---
class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    INSTRUCTIONS = "instructions"

# --- Layout Constants ---
WINDOW_RECT_COORDS = (200, 40, 500, 140)
FLOOR_Y = 220

DESK_X = 300
DESK_Y = FLOOR_Y + 30
DESK_WIDTH = 300

DESKTOP_MONITOR_OFFSET = (140, -55)
LAPTOP_OFFSET = (60, -20)
MUG_OFFSET = (200, -10)

PERSON_SITTING_OFFSET = (120, -50)
PERSON_STANDING_COFFEE_POS = (650, FLOOR_Y + 40)
PERSON_STANDING_POINT_POS = (220, FLOOR_Y + 50)

LIGHT_CONES = [
    (450, 0, 150, 300),
    (100, 0, 100, 250),
    (800, 0, 100, 250),
]

RACK1_POS = (50, FLOOR_Y - 180)
RACK2_POS = (120, FLOOR_Y - 180)
RACK3_POS = (WIDTH - 140, FLOOR_Y - 180)

# --- Colors ---
COLORS = {
    # Environment
    'WALL_DARK': (30, 34, 40),
    'WALL_LIGHT': (40, 44, 50),
    'FLOOR': (25, 28, 32),
    'WINDOW_SKY': (10, 10, 25),

    # Hardware / props
    'SERVER_BODY': (20, 22, 25),
    'MONITOR_BACK': (15, 15, 20),

    # Characters
    'SKIN': (255, 210, 190),
    'COAT': (240, 240, 245),
    'HAIR_A': (60, 40, 20),
    'HAIR_B': (20, 20, 20),
    'HAIR_C': (180, 140, 60),

    # Terminal & text
    'TERM_BG': (10, 15, 10),
    'TERM_FRAME': (40, 60, 40),
    'SCANLINE': (0, 0, 0),
    'TXT_MAIN': (100, 255, 100),
    'TXT_DIM': (40, 160, 40),
    'TXT_ERR': (255, 80, 80),

    # Plots
    'PLOT_AXIS': (0, 100, 0),
    'PLOT_GRID': (0, 40, 0),
    'PLOT_TARG': (0, 255, 255),
    'PLOT_USER': (255, 180, 0),
    
    # New colors for enhanced scenery
    'PLANT_GREEN': (50, 120, 50),
    'PLANT_DARK': (30, 80, 30),
    'COFFEE_BROWN': (100, 60, 40),
    'PARTICLE_GLOW': (150, 200, 255),
}

# --- Safe Math Context ---
ALLOWED_MATH = {
    # Trigonometric functions
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    
    # Hyperbolic functions
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    
    # Exponential and logarithmic
    'sqrt': math.sqrt,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    
    # Rounding and absolute
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'round': round,
    
    # Power
    'pow': pow,
    
    # Constants
    'pi': math.pi,
    'e': math.e,
}

# --- Function Templates by Difficulty ---
FUNCTION_TEMPLATES = {
    'easy': [
        lambda: "sin(x)",
        lambda: "cos(x)",
        lambda: "x",
        lambda: "x ** 2",
    ],
    'medium': [
        lambda: "2 * sin(x)",
        lambda: "cos(x * 2)",
        lambda: "x ** 2 - 3",
        lambda: "sqrt(x + 1)",
        lambda: "log(x + 1)",
        lambda: "sin(x) + cos(x)",
    ],
    'hard': [
        lambda: "sin(x) * cos(x)",
        lambda: "exp(x / 5) - 2",
        lambda: "sin(x ** 2)",
        lambda: "tan(x / 2)",
        lambda: "sqrt(abs(sin(x * 3)))",
        lambda: "log(abs(x) + 1) * sin(x)",
    ],
    'expert': [
        lambda: "sinh(x / 2)",
        lambda: "sin(x) / (x + 1)",
        lambda: "exp(-x) * sin(x * 3)",
        lambda: "atan(x) * 2",
        lambda: "floor(sin(x * 3)) + x / 5",
        lambda: "cosh(x / 3) - 2",
    ],
}


# --- Difficulty Settings ---
DIFFICULTY_LEVELS = {
    'easy': {'threshold': 3, 'points': 100, 'error_tolerance': 0.05},
    'medium': {'threshold': 6, 'points': 200, 'error_tolerance': 0.04},
    'hard': {'threshold': 10, 'points': 300, 'error_tolerance': 0.03},
    'expert': {'threshold': float('inf'), 'points': 500, 'error_tolerance': 0.02},
}

# --- Scoring Constants ---
SKIP_PENALTY: Final[int] = 50
HINT_COST: Final[int] = 0  # No score penalty for hints
INITIAL_HINTS: Final[int] = 3
WIN_ERROR_THRESHOLD: Final[float] = 0.05  # Default win threshold

# --- Gameplay Constants ---
HINT_DISPLAY_DURATION: Final[int] = 300  # frames (5 seconds at 60 FPS)
Y_RANGE_MARGIN: Final[float] = 0.2  # Add 20% margin to y-range for plotting
