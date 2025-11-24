# PlotingGame - Enhanced Edition

A Python-based game where you match mathematical functions by typing expressions. Set in a futuristic science lab with animated visuals.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![Pygame Required](https://img.shields.io/badge/pygame-2.0+-green.svg)

## 🎮 How to Play

1. **Start the Game**: Run the game and navigate the menu with arrow keys
2. **Objective**: Match the target function (cyan curve) by typing a mathematical expression
3. **Type** your function using the keyboard (e.g., `sin(x)`, `x**2`, etc.)
4. **Your Function** (orange curve) updates in real-time as you type!

### Controls

**Menu Navigation:**
- `UP/DOWN` - Navigate menu options
- `ENTER` - Select option

**During Gameplay:**
- Type your mathematical expression directly
- `ENTER` - Advance to next level when matched
- `TAB` - Skip current level (50 point penalty)
- `H` - Get a hint (3 hints available per game)
- `BACKSPACE` - Delete last character
- `ESC` - Pause game

**Paused:**
- `ESC` or `P` - Resume game
- `Q` - Return to main menu

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/MVAD974/PlotingGame.git
cd PlotingGame

# Install dependencies
pip install pygame

# Run the game
python ploting_game.py
# OR
python game.py
```

## 🎯 Features

### Gameplay
- **Progressive Difficulty**: 4 difficulty levels (Easy → Medium → Hard → Expert)
- **Scoring System**: Earn points based on difficulty and accuracy
- **Level Progression**: Advance through increasingly complex functions
- **Hint System**: Get hints when stuck (limited uses)
- **Real-time Feedback**: See error metrics and accuracy as you type

### Enhanced Functions
The game now supports a rich set of mathematical functions:
- **Trigonometric**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- **Hyperbolic**: `sinh`, `cosh`, `tanh`
- **Exponential**: `exp`, `log`, `log10`, `sqrt`
- **Rounding**: `floor`, `ceil`, `round`, `abs`
- **Power**: `pow`, `**` operator
- **Constants**: `pi`, `e`

### Visual Enhancements
- **Animated Lab Scene**: Server racks with dynamic displays, people with animations
- **Enhanced Scenery**: Plants, coffee machine, wall clock, particle effects
- **Twinkling Stars**: Animated night sky visible through the window
- **Dynamic Lighting**: Light cones and glow effects
- **Retro Terminal**: Scanline and vignette effects for authentic feel

## 🏗️ Code Structure

The codebase has been refactored into modular files for better maintainability:

```
PlotingGame/
├── ploting_game.py    # Main entry point (backward compatible)
├── game.py            # Game loop and event handling
├── simulation.py      # Function evaluation and game logic
├── renderer.py        # All rendering and visual effects
├── props.py           # Props and scenery objects (desks, plants, particles)
├── characters.py      # Character drawing and animations
├── config.py          # Configuration, constants, and colors
├── IDEAS.md           # Future improvement ideas
└── README.md          # This file
```

## 🎨 Customization

You can easily customize the game by editing `config.py`:
- Window size and FPS
- Colors and visual theme
- Layout positions
- Available mathematical functions
- Difficulty levels and function templates

## 🔧 Development

### Code Quality
- **Modular Design**: Each module has a single responsibility
- **Type Hints**: Improved code clarity with type annotations
- **Documentation**: Comprehensive docstrings
- **Constants**: No magic numbers, everything configurable

### Adding New Features
1. **New Functions**: Add to `ALLOWED_MATH` in `config.py`
2. **New Props**: Create drawing functions in `props.py`
3. **New Difficulty**: Add templates to `FUNCTION_TEMPLATES` in `config.py`
4. **New Character Poses**: Extend `draw_person()` in `characters.py`

## 📊 Difficulty Levels

| Level | Difficulty | Example Functions |
|-------|-----------|-------------------|
| 1-3   | Easy      | `sin(x)`, `x**2`, `x` |
| 4-6   | Medium    | `2*sin(x)`, `sqrt(x+1)`, `sin(x)+cos(x)` |
| 7-10  | Hard      | `sin(x)*cos(x)`, `tan(x/2)`, `log(abs(x)+1)*sin(x)` |
| 11+   | Expert    | `sinh(x/2)`, `exp(-x)*sin(x*3)`, `floor(sin(x*3))+x/5` |

## 🎓 Educational Value

This game helps develop:
- Understanding of mathematical functions and their graphs
- Pattern recognition and analytical thinking
- Familiarity with function transformations
- Quick mental math and estimation skills

## 🚀 Future Ideas

See [IDEAS.md](IDEAS.md) for a comprehensive list of potential improvements including:
- Sound effects and music
- Achievements and leaderboards
- Tutorial and practice modes
- Multi-player support
- Web and mobile versions
- Advanced visualization options

## 🤝 Contributing

Contributions are welcome! Some areas to contribute:
- Add new mathematical function templates
- Improve visual effects and animations
- Add sound effects
- Create tests for simulation logic
- Optimize rendering performance
- Add accessibility features

## 📝 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Original concept by Marc (@MVAD974)
- Enhanced version with refactoring and new features

## 🐛 Known Issues

None currently. Please report any bugs by creating an issue on GitHub.

---

**Enjoy the game and happy function matching!** 🎉📊🎮
