# -*- coding: utf-8 -*-
"""
Main game loop and orchestration for PlotingGame.
"""

import pygame as pyg
from config import WIDTH, HEIGHT, FPS
from simulation import Simulation
from renderer import Renderer


class Game:
    """Main game class that orchestrates the game loop."""
    
    def __init__(self):
        pyg.init()
        pyg.font.init()
        self.screen = pyg.display.set_mode((WIDTH, HEIGHT))
        pyg.display.set_caption("Science Lab: Function Plotting Challenge")
        self.clock = pyg.time.Clock()
        self.sim = Simulation()
        self.renderer = Renderer(self.screen)
        self.running = True
        self.hint_message = None
        self.hint_timer = 0

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)

        pyg.quit()
    
    def _handle_events(self):
        """Handle all pygame events."""
        for e in pyg.event.get():
            if e.type == pyg.QUIT:
                self.running = False
            elif e.type == pyg.KEYDOWN:
                self._handle_keydown(e)
    
    def _handle_keydown(self, event):
        """Handle keyboard input."""
        if event.key == pyg.K_BACKSPACE:
            self.sim.update_player(self.sim.text_input[:-1])
        elif event.key == pyg.K_RETURN:
            if self.sim.is_win:
                self.sim.new_level()
                self.hint_message = None
        elif event.key == pyg.K_TAB:
            self.sim.skip_level()
            self.hint_message = None
        elif event.key == pyg.K_h:
            # Request a hint
            hint = self.sim.get_hint()
            if hint:
                self.hint_message = hint
                self.hint_timer = 300  # Show for 5 seconds at 60 FPS
            else:
                self.hint_message = "No hints available!"
                self.hint_timer = 180
        else:
            if event.unicode and event.unicode.isprintable():
                self.sim.update_player(self.sim.text_input + event.unicode)
    
    def _update(self):
        """Update game state."""
        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer == 0:
                self.hint_message = None
    
    def _render(self):
        """Render the game."""
        self.renderer.draw_scene(self.sim)
        
        # Display hint if active
        if self.hint_message and self.hint_timer > 0:
            font = pyg.font.SysFont("Arial", 14, bold=True)
            hint_surf = font.render(f"HINT: {self.hint_message}", True, (255, 255, 0))
            hint_bg = pyg.Surface((hint_surf.get_width() + 20, hint_surf.get_height() + 10))
            hint_bg.fill((40, 40, 40))
            hint_bg.set_alpha(200)
            x = (WIDTH - hint_bg.get_width()) // 2
            y = 50
            self.screen.blit(hint_bg, (x, y))
            self.screen.blit(hint_surf, (x + 10, y + 5))
        
        pyg.display.flip()


if __name__ == '__main__':
    Game().run()
