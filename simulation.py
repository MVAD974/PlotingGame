# -*- coding: utf-8 -*-
"""
Simulation logic for PlotingGame.
Handles target function generation, safe evaluation, difficulty management, and win checks.
"""

import math
import random
from typing import List, Tuple, Optional
from config import ALLOWED_MATH, FUNCTION_TEMPLATES


class Simulation:
    """Handles target function generation, safe evaluation, difficulty management, and win checks."""

    def __init__(self):
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
        self.hints_available: int = 3

        self.new_level()

    def new_level(self):
        """Generate a new target function and reset state."""
        # Increase difficulty based on level
        if self.level <= 3:
            self.difficulty = 'easy'
        elif self.level <= 6:
            self.difficulty = 'medium'
        elif self.level <= 10:
            self.difficulty = 'hard'
        else:
            self.difficulty = 'expert'
        
        templates = FUNCTION_TEMPLATES[self.difficulty]
        self.target_formula = random.choice(templates)()
        self.text_input = ""
        self.player_pts = []
        self.is_win = False
        self.current_error = None

        self._calc_target()
        # Debug / dev info – comment out if undesired:
        print(f"Level {self.level} ({self.difficulty}): {self.target_formula}")

    def get_hint(self) -> Optional[str]:
        """Get a hint about the target function if hints are available."""
        if self.hints_available <= 0:
            return None
        
        self.hints_available -= 1
        
        # Provide hints based on what's in the formula
        hints = []
        if 'sin' in self.target_formula:
            hints.append("Uses sine function")
        if 'cos' in self.target_formula:
            hints.append("Uses cosine function")
        if 'tan' in self.target_formula:
            hints.append("Uses tangent function")
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

    def _calc_target(self):
        """Compute target points and adjust plotting y-range."""
        pts, valid, mn, mx = self._calc_points(self.target_formula)
        if not valid:
            return

        self.target_pts = pts
        span = mx - mn or 1.0
        self.y_min = mn - span * 0.2
        self.y_max = mx + span * 0.2

    def update_player(self, text: str):
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

    def _check_win(self):
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

        # Win threshold: tweak as desired
        self.is_win = avg_err < 0.05
        
        if self.is_win:
            # Award points based on difficulty
            points = {'easy': 100, 'medium': 200, 'hard': 300, 'expert': 500}
            self.score += points.get(self.difficulty, 100)
            self.level += 1

    def skip_level(self):
        """Skip current level (penalty to score)."""
        self.score = max(0, self.score - 50)
        self.new_level()
