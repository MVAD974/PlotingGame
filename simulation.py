# -*- coding: utf-8 -*-
"""
Simulation logic for PlotingGame.
Handles target function generation, safe evaluation, difficulty management, and win checks.
"""

import math
import random
from typing import List, Tuple, Optional
from config import (
    ALLOWED_MATH, FUNCTION_TEMPLATES, DIFFICULTY_LEVELS, 
    SKIP_PENALTY, INITIAL_HINTS, WIN_ERROR_THRESHOLD, Y_RANGE_MARGIN
)


class Simulation:
    """Handles target function generation, safe evaluation, difficulty management, and win checks."""

    def __init__(self) -> None:
        # X range and sampling
        self.x_range: Tuple[float, float] = (0, 10)
        self.nb_points: int = 400

        # Target / player data
        self.target_formula: str = ""
        self.target_pts: List[Tuple[float, float]] = []
        self.player_pts: List[Tuple[float, float]] = []

        # Y range for plotting
        self.y_min: float = -5.0
        self.y_max: float = 5.0

        # State
        self.is_valid: bool = True
        self.is_win: bool = False
        self.text_input: str = ""
        self.current_error: Optional[float] = None
        
        # Difficulty and progression
        self.difficulty: str = 'easy'
        self.level: int = 1
        self.score: int = 0
        self.hints_available: int = INITIAL_HINTS

        self.new_level()

    def new_level(self) -> None:
        """Generate a new target function and reset state."""
        # Increase difficulty based on level
        self.difficulty = self._get_difficulty_for_level(self.level)
        
        templates = FUNCTION_TEMPLATES[self.difficulty]
        self.target_formula = random.choice(templates)()
        self.text_input = ""
        self.player_pts = []
        self.is_win = False
        self.current_error = None

        self._calc_target()
        # Debug / dev info – comment out if undesired:
        print(f"Level {self.level} ({self.difficulty}): {self.target_formula}")

    def _get_difficulty_for_level(self, level: int) -> str:
        """Determine difficulty level based on current level number."""
        for difficulty, settings in DIFFICULTY_LEVELS.items():
            if level <= settings['threshold']:
                return difficulty
        return 'expert'  # Fallback to expert for high levels

    def get_hint(self) -> Optional[str]:
        """Get a hint about the target function if hints are available."""
        if self.hints_available <= 0:
            return None
        
        self.hints_available -= 1
        
        # Provide hints based on what's in the formula
        hints = []
        if 'sin' in self.target_formula and 'sinh' not in self.target_formula:
            hints.append("Uses sine function")
        if 'cos' in self.target_formula and 'cosh' not in self.target_formula:
            hints.append("Uses cosine function")
        if 'tan' in self.target_formula and 'tanh' not in self.target_formula:
            hints.append("Uses tangent function")
        if 'sinh' in self.target_formula:
            hints.append("Uses hyperbolic sine")
        if 'cosh' in self.target_formula:
            hints.append("Uses hyperbolic cosine")
        if 'tanh' in self.target_formula:
            hints.append("Uses hyperbolic tangent")
        if 'sqrt' in self.target_formula:
            hints.append("Uses square root")
        if 'log' in self.target_formula:
            hints.append("Uses logarithm")
        if 'exp' in self.target_formula:
            hints.append("Uses exponential")
        if '**' in self.target_formula:
            hints.append("Uses power/exponentiation")
        if '*' in self.target_formula and '**' not in self.target_formula:
            hints.append("Uses multiplication")
        
        if hints:
            return random.choice(hints)
        return "Try basic functions like sin, cos, or polynomials"

    def _calc_points(self, expr: str) -> Tuple[List[Tuple[float, float]], bool, float, float]:
        """
        Evaluate 'expr' safely over x_range and return:
        - points: list[(x, y)]
        - valid: bool (at least one valid point)
        - min_y, max_y across valid points
        """
        expr = expr.strip()
        if not expr:
            return [], False, -5.0, 5.0

        pts = []
        step = (self.x_range[1] - self.x_range[0]) / self.nb_points
        mn, mx = float('inf'), float('-inf')

        for i in range(self.nb_points + 1):
            val_x = self.x_range[0] + i * step

            ctx = dict(ALLOWED_MATH)
            ctx['x'] = val_x

            try:
                val_y = eval(expr, {"__builtins__": {}}, ctx)
            except Exception:
                # Any failure at a single x just skips that point.
                continue

            if isinstance(val_y, complex):
                val_y = val_y.real

            # Filter NaN / inf
            try:
                if math.isnan(val_y) or math.isinf(val_y):
                    continue
            except TypeError:
                continue

            pts.append((val_x, float(val_y)))
            if val_y < mn:
                mn = val_y
            if val_y > mx:
                mx = val_y

        valid = mn != float('inf')
        if not valid:
            mn, mx = -5.0, 5.0
        if mn == mx:
            mn -= 1.0
            mx += 1.0

        return pts, valid, float(mn), float(mx)

    def _calc_target(self) -> None:
        """Compute target points and adjust plotting y-range."""
        pts, valid, mn, mx = self._calc_points(self.target_formula)
        if not valid:
            return

        self.target_pts = pts
        span = mx - mn or 1.0
        self.y_min = mn - span * Y_RANGE_MARGIN
        self.y_max = mx + span * Y_RANGE_MARGIN

    def update_player(self, text: str) -> None:
        """Update player expression, recompute points, and check win."""
        self.text_input = text
        pts, valid, _, _ = self._calc_points(self.text_input)
        self.is_valid = valid

        if valid:
            self.player_pts = pts
            self._check_win()
        else:
            self.player_pts = []
            self.is_win = False
            self.current_error = None

    def _check_win(self) -> None:
        """Compute normalized average error and set win state."""
        if not self.target_pts or not self.player_pts:
            self.is_win = False
            self.current_error = None
            return

        # Use min length to avoid strict equality requirement
        n = min(len(self.target_pts), len(self.player_pts))
        if n == 0:
            self.is_win = False
            self.current_error = None
            return

        span = max(self.y_max - self.y_min, 1e-6)

        total_err = 0.0
        # Assume both lists sampled evenly; compare by index
        for i in range(n):
            ty = self.target_pts[i][1]
            py = self.player_pts[i][1]
            total_err += abs(py - ty) / span

        avg_err = total_err / n
        self.current_error = avg_err

        # Get error threshold for current difficulty
        error_threshold = DIFFICULTY_LEVELS.get(self.difficulty, {}).get('error_tolerance', WIN_ERROR_THRESHOLD)
        self.is_win = avg_err < error_threshold
        
        if self.is_win:
            # Award points based on difficulty
            points = DIFFICULTY_LEVELS.get(self.difficulty, {}).get('points', 100)
            self.score += points
            self.level += 1

    def skip_level(self) -> None:
        """Skip current level (penalty to score)."""
        self.score = max(0, self.score - SKIP_PENALTY)
        self.new_level()
