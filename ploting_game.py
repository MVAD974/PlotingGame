# -*- coding: utf-8 -*-
# @Author  : marc
# @Time    : 24/11/2025 17:01
# @File    : plotting_game.py
# @Project : Tests

import math
import random
import pygame as pyg

# --- Configuration ---
WIDTH, HEIGHT = 900, 700
FPS = 60
H_SPLIT = 400  # Vertical split between lab (top) and terminal (bottom)

# --- Layout constants (previously magic numbers) ---
WINDOW_RECT = pyg.Rect(200, 40, 500, 140)
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
RACK3_POS = (WIDTH - 140, FLOOR_Y - 180)  # double-width rack

# --- Colors ---
C = {
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
}


# --- Safe math context ---
ALLOWED_MATH = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'pi': math.pi,
    'e': math.e,
    'abs': abs,
}


# --- Simulation Logic ---
class Simulation:
    """Handles target function generation, safe evaluation, and win checks."""

    def __init__(self):
        # X range and sampling
        self.x_range = (0, 10)
        self.nb_points = 400

        # Target / player data
        self.target_formula = ""
        self.target_pts = []
        self.player_pts = []

        # Y range for plotting
        self.y_min, self.y_max = -5.0, 5.0

        # State
        self.is_valid = True
        self.is_win = False
        self.text_input = ""
        self.current_error = None  # normalized avg error (0..1 approx)

        self.new_level()

    def new_level(self):
        """Generate a new target function and reset state."""
        funcs = ['sin', 'cos', 'sqrt', 'log']
        coeffs = [2, 3, 5]
        shifts = [1, 2]

        templates = [
            lambda: f"{random.choice(funcs)}(x)",
            lambda: "x ** 2",
            lambda: f"{random.choice(coeffs)} * x",
            lambda: f"x + {random.choice(shifts)}",
            lambda: f"sin(x * {random.choice(coeffs)})",
        ]

        self.target_formula = random.choice(templates)()
        self.text_input = ""
        self.player_pts = []
        self.is_win = False
        self.current_error = None

        self._calc_target()
        # Debug / dev info – comment out if undesired:
        print(f"Target: {self.target_formula}")

    def _calc_points(self, expr):
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

    def update_player(self, text):
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


# --- Renderer ---
class Renderer:
    """Responsible for all drawing and UI rendering."""

    def __init__(self, screen):
        self.screen = screen

        # Fonts
        self.font_term = pyg.font.SysFont("Consolas", 16)
        self.font_term_big = pyg.font.SysFont("Consolas", 22, bold=True)
        self.font_ui = pyg.font.SysFont("Arial", 10)

        # Main regions
        self.rect_lab = pyg.Rect(0, 0, WIDTH, H_SPLIT)
        self.rect_term = pyg.Rect(0, H_SPLIT, WIDTH, HEIGHT - H_SPLIT)

        # Overlays
        self.scanline_surf = self._create_scanlines()
        self.vignette_surf = self._create_vignette()

        # Background stars
        self.stars = [
            (random.randint(200, 700), random.randint(40, 180), random.choice([1, 2]))
            for _ in range(20)
        ]

    def draw_scene(self, sim: Simulation):
        # Top: lab
        self.screen.set_clip(self.rect_lab)
        self._draw_lab_scene(sim)
        self.screen.set_clip(None)

        # Split bar
        pyg.draw.rect(self.screen, (10, 10, 10), (0, H_SPLIT, WIDTH, 6))

        # Bottom: terminal
        self.screen.set_clip(self.rect_term)
        self._draw_terminal_scene(sim)
        self.screen.set_clip(None)

    # --- Lab scene ---

    def _draw_lab_scene(self, sim: Simulation):
        self.screen.fill(C['WALL_DARK'])

        # Window & stars
        pyg.draw.rect(self.screen, C['WINDOW_SKY'], WINDOW_RECT)
        for (sx, sy, sz) in self.stars:
            pyg.draw.circle(self.screen, (200, 200, 255), (sx, sy), sz)
        pyg.draw.rect(self.screen, C['WALL_LIGHT'], WINDOW_RECT, 6)
        pyg.draw.line(
            self.screen,
            C['WALL_LIGHT'],
            (WINDOW_RECT.centerx, WINDOW_RECT.top),
            (WINDOW_RECT.centerx, WINDOW_RECT.bottom),
            4,
        )

        # Floor
        pyg.draw.rect(
            self.screen,
            C['FLOOR'],
            (0, FLOOR_Y, WIDTH, H_SPLIT - FLOOR_Y),
        )

        # Server racks
        self._draw_vector_server(*RACK1_POS, mode=0, sim=sim)
        self._draw_vector_server(*RACK2_POS, mode=1, sim=sim)
        self._draw_vector_server(*RACK3_POS, mode=2, sim=sim, cols=2)

        # Desk & monitor
        self._draw_vector_desk(DESK_X, DESK_Y, DESK_WIDTH)
        mon_x = DESK_X + DESKTOP_MONITOR_OFFSET[0]
        mon_y = DESK_Y + DESKTOP_MONITOR_OFFSET[1]
        self._draw_desktop_monitor(mon_x, mon_y, sim)

        # People
        self._draw_vector_person(
            DESK_X + PERSON_SITTING_OFFSET[0],
            DESK_Y + PERSON_SITTING_OFFSET[1],
            C['HAIR_A'],
            pose="sitting",
        )
        self._draw_vector_person(
            PERSON_STANDING_COFFEE_POS[0],
            PERSON_STANDING_COFFEE_POS[1],
            C['HAIR_B'],
            pose="standing_coffee",
            facing_left=True,
        )
        self._draw_vector_person(
            PERSON_STANDING_POINT_POS[0],
            PERSON_STANDING_POINT_POS[1],
            C['HAIR_C'],
            pose="standing_point",
        )

        # Props
        self._draw_vector_laptop(DESK_X + LAPTOP_OFFSET[0], DESK_Y + LAPTOP_OFFSET[1])
        self._draw_vector_mug(DESK_X + MUG_OFFSET[0], DESK_Y + MUG_OFFSET[1])

        # Light cones
        for x, y, w, h in LIGHT_CONES:
            self._draw_light_cone(x, y, w, h)

    def _draw_vector_server(self, x, y, mode, sim: Simulation, cols=1):
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

    def _draw_desktop_monitor(self, x, y, sim: Simulation):
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

    def _draw_vector_desk(self, x, y, w):
        pyg.draw.polygon(
            self.screen,
            (180, 180, 190),
            [(x, y), (x + w, y), (x + w - 10, y + 40), (x + 10, y + 40)],
        )
        pyg.draw.rect(self.screen, (150, 150, 160), (x + 10, y + 40, w - 20, 5))
        pyg.draw.rect(self.screen, (40, 40, 40), (x + 20, y + 45, 10, 60))
        pyg.draw.rect(self.screen, (40, 40, 40), (x + w - 30, y + 45, 10, 60))

    def _draw_vector_person(self, x, y, hair_col, pose="standing", facing_left=False):
        """Simple vector person with a few poses."""

        def flip(dx):
            return -dx if facing_left else dx

        # Head
        pyg.draw.circle(self.screen, C['SKIN'], (x, y), 12)

        # Hair as an ellipse cap
        hair_rect = pyg.Rect(x - 13, y - 13, 26, 18)
        pyg.draw.ellipse(self.screen, hair_col, hair_rect)

        if pose == "standing_coffee":
            pyg.draw.rect(self.screen, C['COAT'], (x - 10, y + 12, 20, 40), border_radius=5)
            pyg.draw.rect(self.screen, (30, 30, 35), (x - 8, y + 50, 6, 30))
            pyg.draw.rect(self.screen, (30, 30, 35), (x + 2, y + 50, 6, 30))
            arm_end_x, arm_end_y = x + flip(15), y + 25
            pyg.draw.line(self.screen, C['COAT'], (x, y + 15), (arm_end_x, arm_end_y), 6)
            self._draw_vector_mug(arm_end_x, arm_end_y - 5)

        elif pose == "standing_point":
            pyg.draw.rect(self.screen, C['COAT'], (x - 10, y + 12, 20, 40), border_radius=5)
            pyg.draw.rect(self.screen, (30, 30, 35), (x - 8, y + 50, 6, 30))
            pyg.draw.rect(self.screen, (30, 30, 35), (x + 2, y + 50, 6, 30))
            pyg.draw.line(self.screen, C['COAT'], (x, y + 15), (x + 25, y + 10), 6)
            pyg.draw.circle(self.screen, C['SKIN'], (x + 27, y + 10), 3)

        elif pose == "sitting":
            pyg.draw.rect(self.screen, (60, 60, 70), (x - 18, y + 10, 8, 40), border_radius=4)
            pyg.draw.rect(self.screen, C['COAT'], (x - 10, y + 12, 18, 35), border_radius=5)
            pyg.draw.line(self.screen, (30, 30, 35), (x, y + 45), (x + 15, y + 45), 6)
            pyg.draw.line(self.screen, (30, 30, 35), (x + 15, y + 45), (x + 15, y + 65), 6)
            offset = math.sin(pyg.time.get_ticks() / 100) * 2
            pyg.draw.line(self.screen, C['COAT'], (x, y + 20), (x + 15, y + 25 + offset), 5)

    def _draw_vector_laptop(self, x, y):
        pyg.draw.polygon(
            self.screen,
            (20, 20, 20),
            [(x, y), (x + 30, y), (x + 30, y - 20), (x, y - 20)],
        )
        scr_rect = pyg.Rect(x + 2, y - 18, 26, 16)
        pyg.draw.rect(self.screen, (0, 10, 0), scr_rect)

        ticks = pyg.time.get_ticks()
        offset = (ticks // 150) % 8
        for i in range(3):
            ly = scr_rect.y + (i * 5 + offset) % 16
            w_line = (i * 7 + ticks // 50) % 20 + 4
            pyg.draw.line(
                self.screen,
                (0, 255, 0),
                (scr_rect.x + 2, ly),
                (scr_rect.x + 2 + w_line, ly),
            )

        pyg.draw.polygon(
            self.screen,
            (60, 60, 65),
            [(x, y), (x + 30, y), (x + 35, y + 5), (x - 5, y + 5)],
        )

    def _draw_vector_mug(self, x, y):
        pyg.draw.rect(self.screen, (200, 200, 200), (x - 3, y, 6, 8))
        if (pyg.time.get_ticks() // 200) % 2 == 0:
            pyg.draw.line(
                self.screen,
                (255, 255, 255),
                (x, y - 2),
                (x, y - 6),
                1,
            )

    def _draw_light_cone(self, x, y, w, h):
        s = pyg.Surface((WIDTH, H_SPLIT), pyg.SRCALPHA)
        pts = [(x, y), (x - w // 2, y + h), (x + w // 2, y + h)]
        pyg.draw.polygon(s, (255, 255, 200, 10), pts)
        self.screen.blit(s, (0, 0))

    # --- Terminal / plot scene ---

    def _draw_terminal_scene(self, sim: Simulation):
        # Background
        pyg.draw.rect(self.screen, C['TERM_BG'], self.rect_term)

        # Status bar
        pyg.draw.rect(self.screen, C['TERM_FRAME'], (0, H_SPLIT, WIDTH, 30))
        if sim.is_win:
            status = "SYSTEM: MATCH CONFIRMED // UPLOADING DATA..."
            status_col = C['PLOT_USER']
        elif not sim.is_valid and sim.text_input.strip():
            status = "SYSTEM: INPUT ERROR // CHECK SYNTAX / DOMAIN"
            status_col = C['TXT_ERR']
        else:
            status = "SYSTEM: ONLINE // MONITORING..."
            status_col = C['TXT_MAIN']

        lbl = self.font_term.render(status, True, status_col)
        self.screen.blit(lbl, (10, H_SPLIT + 8))

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
        hint_text = "ENTER: validate/next when matched   TAB: skip target   BACKSPACE: edit"
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

    def _draw_grid_and_ticks(self, r, sim: Simulation):
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

    def _draw_curve(self, pts, color, r, sim: Simulation, thick=False):
        if len(pts) < 2:
            return

        span_x = max(sim.x_range[1] - sim.x_range[0], 1e-6)
        span_y = max(sim.y_max - sim.y_min, 1e-6)

        def map_pt(p):
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

    def _create_scanlines(self):
        s = pyg.Surface((WIDTH, HEIGHT - H_SPLIT), pyg.SRCALPHA)
        for y in range(0, HEIGHT - H_SPLIT, 2):
            pyg.draw.line(s, (0, 0, 0, 100), (0, y), (WIDTH, y))
        return s

    def _create_vignette(self):
        s = pyg.Surface((WIDTH, HEIGHT - H_SPLIT), pyg.SRCALPHA)
        w, h = s.get_size()
        pyg.draw.rect(s, (0, 0, 0, 50), (0, 0, w, h), 20)
        return s


# --- Game loop / orchestration ---
class Game:
    def __init__(self):
        pyg.init()
        pyg.font.init()
        self.screen = pyg.display.set_mode((WIDTH, HEIGHT))
        pyg.display.set_caption("Science Lab: Double Rack Edition")
        self.clock = pyg.time.Clock()
        self.sim = Simulation()
        self.renderer = Renderer(self.screen)
        self.running = True

    def run(self):
        while self.running:
            for e in pyg.event.get():
                if e.type == pyg.QUIT:
                    self.running = False
                elif e.type == pyg.KEYDOWN:
                    if e.key == pyg.K_BACKSPACE:
                        self.sim.update_player(self.sim.text_input[:-1])
                    elif e.key == pyg.K_RETURN:
                        if self.sim.is_win:
                            self.sim.new_level()
                    elif e.key == pyg.K_TAB:
                        self.sim.new_level()
                    else:
                        if e.unicode and e.unicode.isprintable():
                            self.sim.update_player(self.sim.text_input + e.unicode)

            self.renderer.draw_scene(self.sim)
            pyg.display.flip()
            self.clock.tick(FPS)

        pyg.quit()


if __name__ == '__main__':
    Game().run()