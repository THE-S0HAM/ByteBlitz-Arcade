# ByteBlitz Arcade

A retro-style arcade games hub built with Python and Pygame.

## Features

- Neon-themed retro GUI interface
- Multiple classic arcade games
- High score tracking and leaderboards
- Customizable settings
- Modular game system for easy expansion

## Games Included

- Snake Reloaded
- Brick Breaker
- UFO Invasion
- Tower Builder
- Coin Dash

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the arcade hub:
   ```
   python hub.py
   ```

## Adding New Games

To add a new game, create a folder in the `games` directory with the following structure:
```
games/your_game_name/
├── main.py         # Game entry point
├── [other_modules] # Game-specific modules
└── assets/         # Game-specific assets
```

The `main.py` file should implement the `Game` class with `start()` and `quit()` methods.