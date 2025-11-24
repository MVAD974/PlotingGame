# -*- coding: utf-8 -*-
"""
Props and objects drawing functions for PlotingGame.
Contains functions to draw desks, monitors, laptops, plants, and other scenery objects.
"""

import random
import pygame as pyg
from typing import List, Tuple
from config import COLORS as C, WIDTH, H_SPLIT


def draw_desk(screen: pyg.Surface, x: int, y: int, w: int) -> None:
    """Draw a vector desk."""
    pyg.draw.polygon(
        screen,
        (180, 180, 190),
        [(x, y), (x + w, y), (x + w - 10, y + 40), (x + 10, y + 40)],
    )
    pyg.draw.rect(screen, (150, 150, 160), (x + 10, y + 40, w - 20, 5))
    pyg.draw.rect(screen, (40, 40, 40), (x + 20, y + 45, 10, 60))
    pyg.draw.rect(screen, (40, 40, 40), (x + w - 30, y + 45, 10, 60))


def draw_laptop(screen: pyg.Surface, x: int, y: int) -> None:
    """Draw a vector laptop with animated screen."""
    pyg.draw.polygon(
        screen,
        (20, 20, 20),
        [(x, y), (x + 30, y), (x + 30, y - 20), (x, y - 20)],
    )
    scr_rect = pyg.Rect(x + 2, y - 18, 26, 16)
    pyg.draw.rect(screen, (0, 10, 0), scr_rect)

    ticks = pyg.time.get_ticks()
    offset = (ticks // 150) % 8
    for i in range(3):
        ly = scr_rect.y + (i * 5 + offset) % 16
        w_line = (i * 7 + ticks // 50) % 20 + 4
        pyg.draw.line(
            screen,
            (0, 255, 0),
            (scr_rect.x + 2, ly),
            (scr_rect.x + 2 + w_line, ly),
        )

    pyg.draw.polygon(
        screen,
        (60, 60, 65),
        [(x, y), (x + 30, y), (x + 35, y + 5), (x - 5, y + 5)],
    )


def draw_mug(screen: pyg.Surface, x: int, y: int) -> None:
    """Draw a coffee mug with steam animation."""
    pyg.draw.rect(screen, (200, 200, 200), (x - 3, y, 6, 8))
    # Animated steam
    if (pyg.time.get_ticks() // 200) % 2 == 0:
        pyg.draw.line(
            screen,
            (255, 255, 255),
            (x, y - 2),
            (x, y - 6),
            1,
        )


def draw_plant(screen: pyg.Surface, x: int, y: int, size: int = 20) -> None:
    """Draw a potted plant."""
    # Pot
    pot_width = size // 2
    pot_height = size // 3
    pyg.draw.polygon(
        screen,
        C['COFFEE_BROWN'],
        [
            (x - pot_width // 2, y),
            (x + pot_width // 2, y),
            (x + pot_width // 3, y + pot_height),
            (x - pot_width // 3, y + pot_height),
        ],
    )
    
    # Leaves - multiple stems
    for i in range(3):
        stem_x = x + (i - 1) * (size // 5)
        stem_height = size + random.randint(-5, 5)
        # Stem
        pyg.draw.line(screen, C['PLANT_DARK'], 
                     (stem_x, y), (stem_x, y - stem_height), 2)
        # Leaves
        pyg.draw.circle(screen, C['PLANT_GREEN'], 
                       (stem_x - 5, y - stem_height + 5), 6)
        pyg.draw.circle(screen, C['PLANT_GREEN'], 
                       (stem_x + 5, y - stem_height + 3), 5)


def draw_coffee_machine(screen: pyg.Surface, x: int, y: int) -> None:
    """Draw a coffee machine."""
    # Main body
    pyg.draw.rect(screen, (80, 80, 90), (x, y, 40, 50), border_radius=3)
    # Display
    pyg.draw.rect(screen, (20, 100, 20), (x + 5, y + 5, 30, 15))
    # Button
    ticks = pyg.time.get_ticks()
    button_col = (255, 100, 100) if (ticks // 500) % 4 == 0 else (150, 50, 50)
    pyg.draw.circle(screen, button_col, (x + 20, y + 30), 5)
    # Drip
    pyg.draw.rect(screen, (60, 40, 30), (x + 15, y + 45, 10, 5))


def draw_clock(screen: pyg.Surface, x: int, y: int, time_seconds: int) -> None:
    """Draw a clock showing game time."""
    radius = 15
    # Clock face
    pyg.draw.circle(screen, (220, 220, 220), (x, y), radius)
    pyg.draw.circle(screen, (40, 40, 40), (x, y), radius, 2)
    
    # Clock hands
    minutes = (time_seconds // 60) % 60
    hours = (time_seconds // 3600) % 12
    
    # Hour hand
    hour_angle = (hours + minutes / 60) * 30 - 90  # 30 degrees per hour
    hour_len = radius * 0.5
    hour_x = x + hour_len * pyg.math.Vector2(1, 0).rotate(hour_angle).x
    hour_y = y + hour_len * pyg.math.Vector2(1, 0).rotate(hour_angle).y
    pyg.draw.line(screen, (40, 40, 40), (x, y), (hour_x, hour_y), 3)
    
    # Minute hand
    minute_angle = minutes * 6 - 90  # 6 degrees per minute
    minute_len = radius * 0.7
    minute_x = x + minute_len * pyg.math.Vector2(1, 0).rotate(minute_angle).x
    minute_y = y + minute_len * pyg.math.Vector2(1, 0).rotate(minute_angle).y
    pyg.draw.line(screen, (40, 40, 40), (x, y), (minute_x, minute_y), 2)
    
    # Center dot
    pyg.draw.circle(screen, (255, 0, 0), (x, y), 3)


def draw_light_cone(screen: pyg.Surface, x: int, y: int, w: int, h: int) -> None:
    """Draw a light cone effect."""
    s = pyg.Surface((WIDTH, H_SPLIT), pyg.SRCALPHA)
    pts: List[Tuple[int, int]] = [(x, y), (x - w // 2, y + h), (x + w // 2, y + h)]
    pyg.draw.polygon(s, (255, 255, 200, 10), pts)
    screen.blit(s, (0, 0))


class Particle:
    """Floating particle for ambient effects."""
    
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.speed_y = random.uniform(-0.3, -0.1)
        self.speed_x = random.uniform(-0.1, 0.1)
        self.lifetime = random.randint(100, 300)
        self.age = 0
        self.size = random.randint(1, 2)
        
    def update(self) -> bool:
        """Update particle position and age. Returns True if particle is still alive."""
        self.x += self.speed_x
        self.y += self.speed_y
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, screen: pyg.Surface) -> None:
        """Draw the particle with fading effect."""
        alpha = int(255 * (1 - self.age / self.lifetime))
        color = (*C['PARTICLE_GLOW'], alpha)
        s = pyg.Surface((self.size * 2, self.size * 2), pyg.SRCALPHA)
        pyg.draw.circle(s, color, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class ParticleSystem:
    """Manages multiple particles for ambient effects."""
    
    def __init__(self) -> None:
        self.particles: List[Particle] = []
        self.spawn_timer = 0
        
    def update(self, spawn_x_range: Tuple[int, int], spawn_y_range: Tuple[int, int]) -> None:
        """Update all particles and spawn new ones."""
        # Update existing particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Spawn new particles occasionally
        self.spawn_timer += 1
        if self.spawn_timer > 20 and len(self.particles) < 30:
            self.spawn_timer = 0
            x = random.uniform(spawn_x_range[0], spawn_x_range[1])
            y = random.uniform(spawn_y_range[0], spawn_y_range[1])
            self.particles.append(Particle(x, y))
            
    def draw(self, screen: pyg.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)
