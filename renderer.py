# -*- coding: utf-8 -*-
"""
Renderer module for PlotingGame.
Handles all drawing and UI rendering with enhanced scenery and effects.
"""

import random
import pygame as pyg
from typing import TYPE_CHECKING, List, Tuple

from config import (
    WIDTH, HEIGHT, H_SPLIT, COLORS as C, 
    WINDOW_RECT_COORDS, FLOOR_Y, DESK_X, DESK_Y, DESK_WIDTH,
    DESKTOP_MONITOR_OFFSET, LAPTOP_OFFSET, MUG_OFFSET,
    PERSON_SITTING_OFFSET, PERSON_STANDING_COFFEE_POS, PERSON_STANDING_POINT_POS,
    LIGHT_CONES, RACK1_POS, RACK2_POS, RACK3_POS
)
from props import (
    draw_desk, draw_laptop, draw_mug, draw_plant, 
    draw_coffee_machine, draw_clock, draw_light_cone,
    ParticleSystem
)
from characters import draw_person

if TYPE_CHECKING:
    from simulation import Simulation


class Renderer:
    """Responsible for all drawing and UI rendering."""

    def __init__(self, screen: pyg.Surface) -> None:
        self.screen = screen

        # Fonts
        self.font_term = pyg.font.SysFont("Consolas", 16)
        self.font_term_big = pyg.font.SysFont("Consolas", 22, bold=True)
        self.font_ui = pyg.font.SysFont("Arial", 10)
        self.font_menu = pyg.font.SysFont("Arial", 24, bold=True)
        self.font_title = pyg.font.SysFont("Arial", 48, bold=True)

        # Main regions
        self.rect_lab = pyg.Rect(0, 0, WIDTH, H_SPLIT)
        self.rect_term = pyg.Rect(0, H_SPLIT, WIDTH, HEIGHT - H_SPLIT)

        # Window rect
        self.window_rect = pyg.Rect(*WINDOW_RECT_COORDS)

        # Overlays
        self.scanline_surf = self._create_scanlines()
        self.vignette_surf = self._create_vignette()

        # Background stars with twinkling
        self.stars = [
            {
                'pos': (random.randint(200, 700), random.randint(40, 180)),
                'size': random.choice([1, 2]),
                'twinkle_offset': random.randint(0, 100)
            }
            for _ in range(25)
        ]
        
        # Particle system for ambient effects
        self.particle_system = ParticleSystem()
        
        # Game start time for clock
        self.start_ticks = pyg.time.get_ticks()

    def draw_scene(self, sim: 'Simulation'):
        # Top: lab
        self.screen.set_clip(self.rect_lab)
        self._draw_lab_scene(sim)
        self.screen.set_clip(None)

        # Split bar with glow effect
        pyg.draw.rect(self.screen, (10, 10, 10), (0, H_SPLIT, WIDTH, 6))
        pyg.draw.rect(self.screen, (0, 100, 0), (0, H_SPLIT + 2, WIDTH, 2))

        # Bottom: terminal
        self.screen.set_clip(self.rect_term)
        self._draw_terminal_scene(sim)
        self.screen.set_clip(None)

    # --- Lab scene ---

    def _draw_lab_scene(self, sim: 'Simulation'):
        self.screen.fill(C['WALL_DARK'])

        # Window with twinkling stars
        pyg.draw.rect(self.screen, C['WINDOW_SKY'], self.window_rect)
        
        ticks = pyg.time.get_ticks()
        for star in self.stars:
            # Twinkling effect
            twinkle = (ticks + star['twinkle_offset']) // 300 % 3
            brightness = 200 + twinkle * 20
            color = (brightness, brightness, 255)
            pyg.draw.circle(self.screen, color, star['pos'], star['size'])
        
        # Window frame
        pyg.draw.rect(self.screen, C['WALL_LIGHT'], self.window_rect, 6)
        pyg.draw.line(
            self.screen,
            C['WALL_LIGHT'],
            (self.window_rect.centerx, self.window_rect.top),
            (self.window_rect.centerx, self.window_rect.bottom),
            4,
        )

        # Floor
        pyg.draw.rect(
            self.screen,
            C['FLOOR'],
            (0, FLOOR_Y, WIDTH, H_SPLIT - FLOOR_Y),
        )

        # Server racks
        self._draw_server_rack(*RACK1_POS, mode=0, sim=sim)
        self._draw_server_rack(*RACK2_POS, mode=1, sim=sim)
        self._draw_server_rack(*RACK3_POS, mode=2, sim=sim, cols=2)

        # Desk & monitor
        draw_desk(self.screen, DESK_X, DESK_Y, DESK_WIDTH)
        mon_x = DESK_X + DESKTOP_MONITOR_OFFSET[0]
        mon_y = DESK_Y + DESKTOP_MONITOR_OFFSET[1]
        self._draw_desktop_monitor(mon_x, mon_y, sim)

        # People
        draw_person(
            self.screen,
            DESK_X + PERSON_SITTING_OFFSET[0],
            DESK_Y + PERSON_SITTING_OFFSET[1],
            C['HAIR_A'],
            pose="sitting",
        )
        draw_person(
            self.screen,
            PERSON_STANDING_COFFEE_POS[0],
            PERSON_STANDING_COFFEE_POS[1],
            C['HAIR_B'],
            pose="standing_coffee",
            facing_left=True,
        )
        draw_person(
            self.screen,
            PERSON_STANDING_POINT_POS[0],
            PERSON_STANDING_POINT_POS[1],
            C['HAIR_C'],
            pose="standing_point",
        )

        # Props
        draw_laptop(self.screen, DESK_X + LAPTOP_OFFSET[0], DESK_Y + LAPTOP_OFFSET[1])
        draw_mug(self.screen, DESK_X + MUG_OFFSET[0], DESK_Y + MUG_OFFSET[1])
        
        # Enhanced scenery - plants
        draw_plant(self.screen, 150, FLOOR_Y + 70, size=25)
        draw_plant(self.screen, WIDTH - 100, FLOOR_Y + 70, size=20)
        
        # Coffee machine
        draw_coffee_machine(self.screen, 700, FLOOR_Y + 30)
        
        # Clock on wall
        elapsed_seconds = (ticks - self.start_ticks) // 1000
        draw_clock(self.screen, 250, 80, elapsed_seconds)

        # Light cones
        for x, y, w, h in LIGHT_CONES:
            draw_light_cone(self.screen, x, y, w, h)
            
        # Particle effects
        self.particle_system.update((50, WIDTH - 50), (0, FLOOR_Y))
        self.particle_system.draw(self.screen)

    def _draw_server_rack(self, x, y, mode, sim: 'Simulation', cols=1):
        """Draw a server rack with dynamic displays."""
        w = 60 * cols
        h = 180

        # Chassis
        pyg.draw.rect(self.screen, C['SERVER_BODY'], (x, y, w, h), border_radius=4)
        pyg.draw.rect(
            self.screen, (40, 44, 50), (x + 4, y + 4, w - 8, h - 8), border_radius=2
        )

        ticks = pyg.time.get_ticks()

        # Screen
        scr_h = 30 if cols == 1 else 60
        screen_rect = pyg.Rect(x + 10, y + 20, w - 20, scr_h)
        pyg.draw.rect(self.screen, (5, 15, 10), screen_rect)

        # Screen glow effect
        glow_surf = pyg.Surface((screen_rect.w + 4, screen_rect.h + 4), pyg.SRCALPHA)
        pyg.draw.rect(glow_surf, (0, 255, 100, 30), glow_surf.get_rect(), border_radius=2)
        self.screen.blit(glow_surf, (screen_rect.x - 2, screen_rect.y - 2))

        # --- Dynamic screens ---

        # Mode 0: Error plot
        if mode == 0:
            if sim.is_valid and sim.player_pts and sim.target_pts:
                pts = []
                step = max(len(sim.target_pts) // 20, 1)
                for i in range(0, len(sim.target_pts), step):
                    diff = sim.player_pts[i][1] - sim.target_pts[i][1]
                    mid_y = screen_rect.centery
                    py = mid_y - (diff * 3)
                    py = max(screen_rect.y + 2, min(screen_rect.bottom - 2, py))
                    px = screen_rect.x + (i / len(sim.target_pts)) * screen_rect.w
                    pts.append((px, py))

                if len(pts) > 1:
                    pyg.draw.lines(self.screen, (255, 100, 100), False, pts, 1)
                    pyg.draw.line(
                        self.screen,
                        (50, 100, 50),
                        (screen_rect.x, screen_rect.centery),
                        (screen_rect.right, screen_rect.centery),
                        1,
                    )
            else:
                pyg.draw.line(
                    self.screen,
                    (50, 50, 50),
                    (screen_rect.x, screen_rect.centery),
                    (screen_rect.right, screen_rect.centery),
                    1,
                )

        # Mode 1: Error bars
        elif mode == 1:
            if sim.is_valid and sim.player_pts and sim.target_pts:
                num_bars = 5
                gap = 2
                bar_w = (screen_rect.w - (num_bars * gap)) / num_bars
                chunk_s = max(len(sim.target_pts) // num_bars, 1)

                for i in range(num_bars):
                    err_sum = 0.0
                    count = 0
                    for j in range(i * chunk_s, (i + 1) * chunk_s):
                        if j < len(sim.target_pts) and j < len(sim.player_pts):
                            err_sum += abs(
                                sim.player_pts[j][1] - sim.target_pts[j][1]
                            )
                            count += 1
                    avg_err = err_sum / count if count > 0 else 0.0
                    h_factor = max(0.0, 1.0 - (avg_err / 2.0))
                    bh = int(h_factor * (screen_rect.h - 2))
                    if h_factor > 0.8:
                        col = (0, 255, 0)
                    elif h_factor > 0.4:
                        col = (255, 255, 0)
                    else:
                        col = (255, 0, 0)

                    bx = screen_rect.x + gap + i * (bar_w + gap)
                    pyg.draw.rect(
                        self.screen,
                        col,
                        (bx, screen_rect.bottom - bh, bar_w, bh),
                    )
            else:
                idx = (ticks // 300) % 5
                bx = screen_rect.x + 5 + idx * 8
                pyg.draw.rect(
                    self.screen,
                    (100, 100, 100),
                    (bx, screen_rect.bottom - 5, 6, 5),
                )

        # Mode 2: Target scan
        elif mode == 2:
            pts = []
            if sim.target_pts:
                step = 5 if cols == 2 else 10
                span_y = max(sim.y_max - sim.y_min, 1e-6)
                for i in range(0, len(sim.target_pts), step):
                    y_val = sim.target_pts[i][1]
                    y_norm = (y_val - sim.y_min) / span_y
                    py = screen_rect.bottom - y_norm * screen_rect.h
                    px = screen_rect.x + (i / len(sim.target_pts)) * screen_rect.w
                    pts.append((px, py))

                if len(pts) > 1:
                    pyg.draw.lines(self.screen, (0, 200, 255), False, pts, 1)

                # Moving scanline
                sx = (ticks // 30) % int(screen_rect.w)
                pyg.draw.line(
                    self.screen,
                    (255, 255, 255),
                    (screen_rect.x + sx, screen_rect.y),
                    (screen_rect.x + sx, screen_rect.bottom),
                    1,
                )

        # --- Blinking lights under the screen ---

        start_y = y + 20 + scr_h + 10
        for c in range(cols):
            col_x = x + 10 + (c * 60)
            for i in range(5):
                ly = start_y + i * 20
                if ly > y + h - 10:
                    break

                is_on = (ticks // 600 + i * 2 + mode + c) % 3 == 0
                col = (0, 255, 100) if is_on else (40, 60, 40)
                pyg.draw.rect(self.screen, col, (col_x, ly, 30, 4))

                if (ticks // 300 + i + c) % 4 == 0:
                    pyg.draw.circle(
                        self.screen, (50, 150, 255), (col_x + 40, ly + 2), 2
                    )

    def _draw_desktop_monitor(self, x, y, sim: 'Simulation'):
        """Draw desktop monitor with mini plot."""
        # Stand
        pyg.draw.rect(self.screen, (30, 30, 35), (x + 25, y + 40, 10, 10))
        pyg.draw.rect(self.screen, (30, 30, 35), (x + 15, y + 50, 30, 2))

        # Body
        w, h = 60, 40
        pyg.draw.rect(self.screen, C['MONITOR_BACK'], (x, y, w, h), border_radius=3)
        screen_rect = pyg.Rect(x + 2, y + 2, w - 4, h - 4)
        pyg.draw.rect(self.screen, (0, 0, 0), screen_rect)

        # Mini plot inside monitor
        self.screen.set_clip(screen_rect)
        pyg.draw.line(
            self.screen,
            (0, 50, 0),
            (screen_rect.centerx, screen_rect.y),
            (screen_rect.centerx, screen_rect.bottom),
        )
        pyg.draw.line(
            self.screen,
            (0, 50, 0),
            (screen_rect.x, screen_rect.centery),
            (screen_rect.right, screen_rect.centery),
        )

        self._draw_curve(sim.target_pts, C['PLOT_TARG'], screen_rect, sim, thick=False)
        self._draw_curve(sim.player_pts, C['PLOT_USER'], screen_rect, sim, thick=False)

        self.screen.set_clip(self.rect_lab)

    # --- Terminal / plot scene ---

    def _draw_terminal_scene(self, sim: 'Simulation'):
        # Background
        pyg.draw.rect(self.screen, C['TERM_BG'], self.rect_term)

        # Status bar with score and level
        pyg.draw.rect(self.screen, C['TERM_FRAME'], (0, H_SPLIT, WIDTH, 30))
        
        if sim.is_win:
            status = "SYSTEM: MATCH CONFIRMED // UPLOADING DATA..."
            status_col = C['PLOT_USER']
        elif not sim.is_valid and sim.text_input.strip():
            status = "SYSTEM: INPUT ERROR // CHECK SYNTAX / DOMAIN"
            status_col = C['TXT_ERR']
        else:
            status = f"SYSTEM: ONLINE // LEVEL: {sim.level} // SCORE: {sim.score}"
            status_col = C['TXT_MAIN']

        lbl = self.font_term.render(status, True, status_col)
        self.screen.blit(lbl, (10, H_SPLIT + 8))
        
        # Difficulty indicator
        diff_text = f"DIFFICULTY: {sim.difficulty.upper()}"
        diff_surf = self.font_ui.render(diff_text, True, C['TXT_DIM'])
        self.screen.blit(diff_surf, (WIDTH - diff_surf.get_width() - 10, H_SPLIT + 10))

        margin_x, margin_y = 80, 60
        plot_rect = pyg.Rect(
            margin_x,
            H_SPLIT + margin_y,
            WIDTH - margin_x * 2,
            180,
        )

        # Plot area
        pyg.draw.rect(self.screen, (5, 10, 5), plot_rect)
        pyg.draw.rect(self.screen, C['TERM_FRAME'], plot_rect.inflate(4, 4), 2)
        self._draw_grid_and_ticks(plot_rect, sim)

        self.screen.set_clip(plot_rect)
        self._draw_curve(sim.target_pts, C['PLOT_TARG'], plot_rect, sim, thick=False)
        self._draw_curve(sim.player_pts, C['PLOT_USER'], plot_rect, sim, thick=True)
        self.screen.set_clip(None)

        # Command input
        cmd_y = HEIGHT - 50
        prompt = self.font_term_big.render("USER_INPUT >", True, C['TXT_DIM'])
        self.screen.blit(prompt, (margin_x, cmd_y))

        col = C['TXT_MAIN'] if sim.is_valid or not sim.text_input else C['TXT_ERR']
        inp = self.font_term_big.render(sim.text_input, True, col)
        self.screen.blit(inp, (margin_x + 160, cmd_y))

        # Caret
        if (pyg.time.get_ticks() // 500) % 2 == 0:
            caret_x = margin_x + 160 + inp.get_width()
            pyg.draw.rect(self.screen, col, (caret_x, cmd_y, 12, 22))

        # Hints / help text
        hint_text = f"ENTER: validate/next   TAB: skip   H: hint({sim.hints_available} left)   BACKSPACE: edit"
        hint_surf = self.font_ui.render(hint_text, True, C['TXT_DIM'])
        self.screen.blit(
            hint_surf,
            (margin_x, plot_rect.bottom + 35),
        )

        # Error readout
        if sim.current_error is not None and sim.is_valid:
            err_text = f"AVG NORMALIZED ERROR: {sim.current_error:.3f}"
            err_col = C['TXT_MAIN'] if not sim.is_win else C['PLOT_USER']
            err_surf = self.font_ui.render(err_text, True, err_col)
            self.screen.blit(err_surf, (plot_rect.right - err_surf.get_width(), plot_rect.y - 18))

        # Overlays
        self.screen.blit(self.scanline_surf, (0, H_SPLIT))
        self.screen.blit(self.vignette_surf, (0, H_SPLIT))

    def _draw_grid_and_ticks(self, r: pyg.Rect, sim: 'Simulation') -> None:
        """Draw grid and axis labels."""
        steps_x = 10
        for i in range(steps_x + 1):
            f = i / steps_x
            x = r.x + f * r.w
            val = sim.x_range[0] + f * (sim.x_range[1] - sim.x_range[0])
            pyg.draw.line(self.screen, C['PLOT_GRID'], (x, r.y), (x, r.bottom), 1)
            lbl = self.font_ui.render(f"{val:.1f}", True, C['TXT_DIM'])
            self.screen.blit(lbl, (x - lbl.get_width() / 2, r.bottom + 5))

        steps_y = 5
        for i in range(steps_y + 1):
            f = i / steps_y
            y = r.bottom - f * r.h
            val = sim.y_min + f * (sim.y_max - sim.y_min)
            pyg.draw.line(self.screen, C['PLOT_GRID'], (r.x, y), (r.right, y), 1)
            lbl = self.font_ui.render(f"{val:.1f}", True, C['TXT_DIM'])
            self.screen.blit(lbl, (r.x - lbl.get_width() - 8, y - 6))

    def _draw_curve(
        self, 
        pts: List[Tuple[float, float]], 
        color: Tuple[int, int, int], 
        r: pyg.Rect, 
        sim: 'Simulation', 
        thick: bool = False
    ) -> None:
        """Draw a curve on the plot."""
        if len(pts) < 2:
            return

        span_x = max(sim.x_range[1] - sim.x_range[0], 1e-6)
        span_y = max(sim.y_max - sim.y_min, 1e-6)

        def map_pt(p: Tuple[float, float]) -> Tuple[float, float]:
            xn = (p[0] - sim.x_range[0]) / span_x
            yn = (p[1] - sim.y_min) / span_y
            return (r.x + xn * r.w, r.bottom - yn * r.h)

        scr_pts = [map_pt(p) for p in pts]

        pyg.draw.aalines(self.screen, color, False, scr_pts)
        if thick:
            pyg.draw.aalines(
                self.screen,
                color,
                False,
                [(x, y + 1) for (x, y) in scr_pts],
            )

    def _create_scanlines(self) -> pyg.Surface:
        """Create scanline overlay effect."""
        s = pyg.Surface((WIDTH, HEIGHT - H_SPLIT), pyg.SRCALPHA)
        for y in range(0, HEIGHT - H_SPLIT, 2):
            pyg.draw.line(s, (0, 0, 0, 100), (0, y), (WIDTH, y))
        return s

    def _create_vignette(self) -> pyg.Surface:
        """Create vignette overlay effect."""
        s = pyg.Surface((WIDTH, HEIGHT - H_SPLIT), pyg.SRCALPHA)
        w, h = s.get_size()
        pyg.draw.rect(s, (0, 0, 0, 50), (0, 0, w, h), 20)
        return s
    
    # --- Menu and UI Screens ---
    
    def draw_menu(self, selection: int) -> None:
        """Draw the main menu screen."""
        self.screen.fill((10, 15, 20))
        
        # Title
        title = self.font_title.render("PLOTTING GAME", True, C['PLOT_TARG'])
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_menu.render("Science Lab: Function Matching Challenge", True, C['TXT_DIM'])
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = ["Play", "Instructions", "Quit"]
        start_y = 300
        spacing = 60
        
        for i, option in enumerate(options):
            color = C['PLOT_USER'] if i == selection else C['TXT_MAIN']
            prefix = "> " if i == selection else "  "
            text = self.font_menu.render(f"{prefix}{option}", True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, start_y + i * spacing))
            self.screen.blit(text, text_rect)
        
        # Controls hint
        hint = self.font_ui.render("Use UP/DOWN arrows to navigate, ENTER to select", True, C['TXT_DIM'])
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(hint, hint_rect)
    
    def draw_instructions(self) -> None:
        """Draw the instructions screen."""
        self.screen.fill((10, 15, 20))
        
        # Title
        title = self.font_title.render("HOW TO PLAY", True, C['PLOT_TARG'])
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "OBJECTIVE:",
            "  Match the target function (cyan curve) by typing a mathematical expression.",
            "",
            "CONTROLS:",
            "  Type your function using the keyboard (e.g., sin(x), x**2, etc.)",
            "  ENTER - Advance to next level when matched",
            "  TAB - Skip current level (score penalty)",
            "  H - Get a hint (limited hints available)",
            "  BACKSPACE - Delete character",
            "  ESC - Pause game",
            "",
            "AVAILABLE FUNCTIONS:",
            "  Trigonometric: sin, cos, tan, asin, acos, atan",
            "  Hyperbolic: sinh, cosh, tanh",
            "  Exponential: exp, log, log10, sqrt",
            "  Other: abs, floor, ceil, round, pow",
            "  Constants: pi, e",
            "",
            "DIFFICULTY:",
            "  The game gets progressively harder with more complex functions.",
            "  Easy (Levels 1-3) → Medium (4-6) → Hard (7-10) → Expert (11+)",
        ]
        
        start_y = 140
        line_height = 22
        
        for i, line in enumerate(instructions):
            if line.endswith(":"):
                color = C['PLOT_USER']
                font = pyg.font.SysFont("Arial", 12, bold=True)
            elif line.startswith("  "):
                color = C['TXT_MAIN']
                font = pyg.font.SysFont("Arial", 10)
            else:
                color = C['TXT_DIM']
                font = pyg.font.SysFont("Arial", 10)
            
            text = font.render(line, True, color)
            self.screen.blit(text, (100, start_y + i * line_height))
        
        # Back hint
        hint = self.font_menu.render("Press ESC or ENTER to return", True, C['TXT_DIM'])
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(hint, hint_rect)
    
    def draw_pause_overlay(self) -> None:
        """Draw pause overlay on top of game screen."""
        # Semi-transparent overlay
        overlay = pyg.Surface((WIDTH, HEIGHT), pyg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        title = self.font_title.render("PAUSED", True, C['PLOT_TARG'])
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(title, title_rect)
        
        # Options
        options = [
            "ESC or P - Resume",
            "Q - Return to Menu",
        ]
        
        start_y = HEIGHT // 2 + 20
        for i, option in enumerate(options):
            text = self.font_menu.render(option, True, C['TXT_MAIN'])
            text_rect = text.get_rect(center=(WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
    
    def draw_game_over(self, score: int, level: int) -> None:
        """Draw game over screen."""
        self.screen.fill((10, 15, 20))
        
        # Title
        title = self.font_title.render("GAME OVER", True, C['TXT_ERR'])
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Stats
        stats = [
            f"Final Score: {score}",
            f"Level Reached: {level}",
        ]
        
        start_y = 280
        for i, stat in enumerate(stats):
            text = self.font_menu.render(stat, True, C['PLOT_USER'])
            text_rect = text.get_rect(center=(WIDTH // 2, start_y + i * 50))
            self.screen.blit(text, text_rect)
        
        # Continue hint
        hint = self.font_menu.render("Press ENTER to return to menu", True, C['TXT_DIM'])
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.screen.blit(hint, hint_rect)
