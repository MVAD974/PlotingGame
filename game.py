# -*- coding: utf-8 -*-
"""
Main game loop and orchestration for PlotingGame.
Handles game states, input processing, updates, and rendering coordination.
"""

import pygame as pyg
from typing import Optional
import random
from config import (
    WIDTH, HEIGHT, FPS, GameState, HINT_DISPLAY_DURATION,
    SCREEN_SHAKE_DURATION, SCREEN_SHAKE_INTENSITY, FLASH_DURATION, FLASH_COLOR
)
from simulation import Simulation
from renderer import Renderer


class Game:
    """Main game class that orchestrates the game loop and manages game states."""
    
    def __init__(self) -> None:
        """Initialize pygame and game components."""
        pyg.init()
        pyg.font.init()
        self.screen = pyg.display.set_mode((WIDTH, HEIGHT))
        pyg.display.set_caption("Science Lab: Function Plotting Challenge")
        self.clock = pyg.time.Clock()
        
        # Game components
        self.sim = Simulation()
        self.renderer = Renderer(self.screen)
        
        # Game state
        self.state: GameState = GameState.MENU
        self.running: bool = True
        
        # UI state
        self.hint_message: Optional[str] = None
        self.hint_timer: int = 0
        self.menu_selection: int = 0  # 0=Play, 1=Instructions, 2=Quit
        
        # Visual effects
        self.screen_shake_timer: int = 0
        self.flash_timer: int = 0
        self.shake_offset: tuple[int, int] = (0, 0)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self._process_input()
            self._update_logic()
            self._render_frame()
            self.clock.tick(FPS)

        pyg.quit()
    
    def _process_input(self) -> None:
        """Process all input events based on current game state."""
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                self.running = False
            elif event.type == pyg.KEYDOWN:
                self._handle_keydown(event)
    
    def _handle_keydown(self, event: pyg.event.Event) -> None:
        """Handle keyboard input based on current game state."""
        if self.state == GameState.MENU:
            self._handle_menu_input(event)
        elif self.state == GameState.INSTRUCTIONS:
            self._handle_instructions_input(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_input(event)
        elif self.state == GameState.PAUSED:
            self._handle_paused_input(event)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_input(event)
    
    def _handle_menu_input(self, event: pyg.event.Event) -> None:
        """Handle input in menu state."""
        if event.key == pyg.K_UP:
            self.menu_selection = (self.menu_selection - 1) % 3
        elif event.key == pyg.K_DOWN:
            self.menu_selection = (self.menu_selection + 1) % 3
        elif event.key == pyg.K_RETURN or event.key == pyg.K_SPACE:
            if self.menu_selection == 0:  # Play
                self.state = GameState.PLAYING
                self.sim = Simulation()  # Reset game
            elif self.menu_selection == 1:  # Instructions
                self.state = GameState.INSTRUCTIONS
            elif self.menu_selection == 2:  # Quit
                self.running = False
    
    def _handle_instructions_input(self, event: pyg.event.Event) -> None:
        """Handle input in instructions state."""
        if event.key == pyg.K_ESCAPE or event.key == pyg.K_RETURN:
            self.state = GameState.MENU
    
    def _handle_playing_input(self, event: pyg.event.Event) -> None:
        """Handle input during gameplay."""
        if event.key == pyg.K_ESCAPE:
            self.state = GameState.PAUSED
        elif event.key == pyg.K_BACKSPACE:
            self.sim.update_player(self.sim.text_input[:-1])
        elif event.key == pyg.K_RETURN:
            if self.sim.is_win:
                # Trigger visual effects for level completion
                self._trigger_level_complete_effects()
                self.sim.new_level()
                self.hint_message = None
        elif event.key == pyg.K_TAB:
            self.sim.skip_level()
            self.hint_message = None
        elif event.key == pyg.K_h:
            self._request_hint()
        else:
            if event.unicode and event.unicode.isprintable():
                self.sim.update_player(self.sim.text_input + event.unicode)
    
    def _trigger_level_complete_effects(self) -> None:
        """Trigger visual effects when player completes a level."""
        self.screen_shake_timer = SCREEN_SHAKE_DURATION
        self.flash_timer = FLASH_DURATION
    
    def _handle_paused_input(self, event: pyg.event.Event) -> None:
        """Handle input when paused."""
        if event.key == pyg.K_ESCAPE or event.key == pyg.K_p:
            self.state = GameState.PLAYING
        elif event.key == pyg.K_q:
            self.state = GameState.MENU
    
    def _handle_game_over_input(self, event: pyg.event.Event) -> None:
        """Handle input in game over state."""
        if event.key == pyg.K_RETURN or event.key == pyg.K_SPACE:
            self.state = GameState.MENU
        elif event.key == pyg.K_ESCAPE:
            self.running = False
    
    def _request_hint(self) -> None:
        """Request and display a hint."""
        hint = self.sim.get_hint()
        if hint:
            self.hint_message = hint
            self.hint_timer = HINT_DISPLAY_DURATION
        else:
            self.hint_message = "No hints available!"
            self.hint_timer = HINT_DISPLAY_DURATION // 2
    
    def _update_logic(self) -> None:
        """Update game logic based on current state."""
        if self.state == GameState.PLAYING:
            self._update_playing()
    
    def _update_playing(self) -> None:
        """Update logic during gameplay."""
        # Update hint timer
        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer == 0:
                self.hint_message = None
        
        # Update screen shake
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1
            intensity = SCREEN_SHAKE_INTENSITY * (self.screen_shake_timer / SCREEN_SHAKE_DURATION)
            self.shake_offset = (
                random.randint(-int(intensity), int(intensity)),
                random.randint(-int(intensity), int(intensity))
            )
        else:
            self.shake_offset = (0, 0)
        
        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1
    
    def _render_frame(self) -> None:
        """Render the current frame based on game state."""
        # Create a temporary surface for shake effect
        if self.state == GameState.PLAYING and self.shake_offset != (0, 0):
            temp_surface = pyg.Surface((WIDTH, HEIGHT))
            original_screen = self.screen
            self.screen = temp_surface
        
        # Render current state
        if self.state == GameState.MENU:
            self.renderer.draw_menu(self.menu_selection)
        elif self.state == GameState.INSTRUCTIONS:
            self.renderer.draw_instructions()
        elif self.state == GameState.PLAYING:
            self.renderer.draw_scene(self.sim)
            self._draw_hint_overlay()
            self._draw_flash_effect()
        elif self.state == GameState.PAUSED:
            self.renderer.draw_scene(self.sim)
            self.renderer.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.sim.score, self.sim.level)
        
        # Apply screen shake if active
        if self.state == GameState.PLAYING and self.shake_offset != (0, 0):
            self.screen = original_screen
            self.screen.fill((0, 0, 0))
            self.screen.blit(temp_surface, self.shake_offset)
        
        pyg.display.flip()
    
    def _draw_flash_effect(self) -> None:
        """Draw flash effect overlay when active."""
        if self.flash_timer > 0:
            alpha = int(255 * (self.flash_timer / FLASH_DURATION))
            flash_surf = pyg.Surface((WIDTH, HEIGHT), pyg.SRCALPHA)
            color_with_alpha = (*FLASH_COLOR[:3], min(alpha, FLASH_COLOR[3]))
            flash_surf.fill(color_with_alpha)
            self.screen.blit(flash_surf, (0, 0))
    
    def _draw_hint_overlay(self) -> None:
        """Draw hint message overlay if active."""
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


if __name__ == '__main__':
    Game().run()
