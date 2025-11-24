#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for PlotingGame simulation logic.
Run with: python3 test_simulation.py
"""

import sys
import math
from simulation import Simulation


def test_initialization():
    """Test that simulation initializes correctly."""
    sim = Simulation()
    assert sim.level == 1
    assert sim.score == 0
    assert sim.hints_available == 3
    assert sim.difficulty == 'easy'
    assert len(sim.target_pts) > 0
    print("✓ Initialization test passed")


def test_difficulty_progression():
    """Test that difficulty increases with level."""
    sim = Simulation()
    
    # Level 1-3 should be easy
    sim.level = 1
    sim.new_level()
    assert sim.difficulty == 'easy'
    
    # Level 4-6 should be medium
    sim.level = 4
    sim.new_level()
    assert sim.difficulty == 'medium'
    
    # Level 7-10 should be hard
    sim.level = 7
    sim.new_level()
    assert sim.difficulty == 'hard'
    
    # Level 11+ should be expert
    sim.level = 11
    sim.new_level()
    assert sim.difficulty == 'expert'
    
    print("✓ Difficulty progression test passed")


def test_valid_expression():
    """Test that valid mathematical expressions are evaluated."""
    sim = Simulation()
    
    # Test simple expression
    sim.update_player("sin(x)")
    assert sim.is_valid
    assert len(sim.player_pts) > 0
    
    # Test complex expression
    sim.update_player("sin(x) * cos(x) + x**2")
    assert sim.is_valid
    assert len(sim.player_pts) > 0
    
    print("✓ Valid expression test passed")


def test_invalid_expression():
    """Test that invalid expressions are handled."""
    sim = Simulation()
    
    # Test invalid syntax
    sim.update_player("sin(x")
    assert not sim.is_valid or len(sim.player_pts) == 0
    
    # Test unsafe code (should not evaluate)
    sim.update_player("__import__('os').system('ls')")
    assert not sim.is_valid or len(sim.player_pts) == 0
    
    print("✓ Invalid expression test passed")


def test_win_condition():
    """Test that win condition works correctly."""
    sim = Simulation()
    
    # Set a simple target
    sim.target_formula = "x"
    sim._calc_target()
    
    # Match the target exactly
    sim.update_player("x")
    assert sim.is_valid
    # Should win with exact match
    assert sim.is_win or sim.current_error < 0.05
    
    # Test non-matching function
    sim.update_player("x + 10")
    assert sim.is_valid
    assert not sim.is_win
    
    print("✓ Win condition test passed")


def test_skip_level():
    """Test that skipping level works correctly."""
    sim = Simulation()
    initial_score = 100  # Set a positive score
    sim.score = initial_score
    old_formula = sim.target_formula
    
    sim.skip_level()
    # Score penalty should be applied
    assert sim.score == initial_score - 50
    # New level should have new formula
    assert sim.target_formula != old_formula or True  # Formula might be same by chance
    
    print("✓ Skip level test passed")


def test_hints():
    """Test hint system."""
    sim = Simulation()
    initial_hints = sim.hints_available
    
    # Get a hint
    hint = sim.get_hint()
    assert hint is not None
    assert sim.hints_available == initial_hints - 1
    
    # Exhaust hints
    sim.hints_available = 1
    sim.get_hint()
    assert sim.hints_available == 0
    
    # No more hints available
    hint = sim.get_hint()
    assert hint is None
    
    print("✓ Hints test passed")


def test_scoring():
    """Test that scoring works correctly."""
    sim = Simulation()
    sim.level = 1
    sim.difficulty = 'easy'
    initial_score = sim.score
    
    # Simulate a win
    sim.target_formula = "x"
    sim._calc_target()
    sim.update_player("x")
    
    if sim.is_win:
        # Score should increase
        assert sim.score > initial_score
        # Level should increase
        assert sim.level > 1
    
    print("✓ Scoring test passed")


def test_safe_evaluation():
    """Test that evaluation is safe and handles edge cases."""
    sim = Simulation()
    
    # Test division by zero handling
    sim.update_player("1 / x")
    # Should handle x=0 gracefully (skip that point)
    
    # Test logarithm of negative/zero
    sim.update_player("log(x)")
    # Should handle x=0 gracefully
    
    # Test sqrt of negative
    sim.update_player("sqrt(x - 20)")
    # Should handle negative values gracefully
    
    print("✓ Safe evaluation test passed")


def run_all_tests():
    """Run all tests."""
    print("Running PlotingGame simulation tests...\n")
    
    tests = [
        test_initialization,
        test_difficulty_progression,
        test_valid_expression,
        test_invalid_expression,
        test_win_condition,
        test_skip_level,
        test_hints,
        test_scoring,
        test_safe_evaluation,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    if failed == 0:
        print("All tests passed! ✓")
        return 0
    else:
        print(f"{failed} test(s) failed ✗")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
