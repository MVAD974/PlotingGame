# -*- coding: utf-8 -*-
"""
Character drawing functions for PlotingGame.
Contains functions to draw people with different poses and animations.
"""

import math
import pygame as pyg
from typing import Tuple
from config import COLORS as C


def draw_person(
    screen: pyg.Surface, 
    x: int, 
    y: int, 
    hair_col: Tuple[int, int, int], 
    pose: str = "standing", 
    facing_left: bool = False
) -> None:
    """
    Draw a vector person with various poses.
    
    Args:
        screen: Pygame screen surface
        x: X position coordinate
        y: Y position coordinate
        hair_col: RGB tuple for hair color
        pose: Pose type - "standing", "sitting", "standing_coffee", "standing_point"
        facing_left: Whether the person faces left
    """
    def flip(dx: int) -> int:
        """Flip horizontal offset if facing left."""
        return -dx if facing_left else dx

    # Head
    pyg.draw.circle(screen, C['SKIN'], (x, y), 12)

    # Hair as an ellipse cap
    hair_rect = pyg.Rect(x - 13, y - 13, 26, 18)
    pyg.draw.ellipse(screen, hair_col, hair_rect)

    if pose == "standing_coffee":
        pyg.draw.rect(screen, C['COAT'], (x - 10, y + 12, 20, 40), border_radius=5)
        pyg.draw.rect(screen, (30, 30, 35), (x - 8, y + 50, 6, 30))
        pyg.draw.rect(screen, (30, 30, 35), (x + 2, y + 50, 6, 30))
        arm_end_x, arm_end_y = x + flip(15), y + 25
        pyg.draw.line(screen, C['COAT'], (x, y + 15), (arm_end_x, arm_end_y), 6)
        from props import draw_mug
        draw_mug(screen, arm_end_x, arm_end_y - 5)

    elif pose == "standing_point":
        pyg.draw.rect(screen, C['COAT'], (x - 10, y + 12, 20, 40), border_radius=5)
        pyg.draw.rect(screen, (30, 30, 35), (x - 8, y + 50, 6, 30))
        pyg.draw.rect(screen, (30, 30, 35), (x + 2, y + 50, 6, 30))
        pyg.draw.line(screen, C['COAT'], (x, y + 15), (x + 25, y + 10), 6)
        pyg.draw.circle(screen, C['SKIN'], (x + 27, y + 10), 3)

    elif pose == "sitting":
        # Chair back
        pyg.draw.rect(screen, (60, 60, 70), (x - 18, y + 10, 8, 40), border_radius=4)
        # Body
        pyg.draw.rect(screen, C['COAT'], (x - 10, y + 12, 18, 35), border_radius=5)
        # Legs
        pyg.draw.line(screen, (30, 30, 35), (x, y + 45), (x + 15, y + 45), 6)
        pyg.draw.line(screen, (30, 30, 35), (x + 15, y + 45), (x + 15, y + 65), 6)
        # Animated arm typing
        offset = math.sin(pyg.time.get_ticks() / 100) * 2
        pyg.draw.line(screen, C['COAT'], (x, y + 20), (x + 15, y + 25 + offset), 5)
        
    elif pose == "standing":
        # Basic standing pose
        pyg.draw.rect(screen, C['COAT'], (x - 10, y + 12, 20, 40), border_radius=5)
        pyg.draw.rect(screen, (30, 30, 35), (x - 8, y + 50, 6, 30))
        pyg.draw.rect(screen, (30, 30, 35), (x + 2, y + 50, 6, 30))
        # Arms at sides
        pyg.draw.line(screen, C['COAT'], (x - 5, y + 15), (x - 15, y + 35), 5)
        pyg.draw.line(screen, C['COAT'], (x + 5, y + 15), (x + 15, y + 35), 5)
