import os
import importlib.util
import sys

class GameLoader:
    """Loads and manages games from the games directory"""
    
    def __init__(self):
        self.games = {}
        self.games_path = "games"
        
    def discover_games(self):
        """Scan the games directory and load available games"""
        if not os.path.exists(self.games_path):
            print(f"Error: Games directory '{self.games_path}' not found")
            return {}
            
        # Look for game directories
        for game_dir in os.listdir(self.games_path):
            game_path = os.path.join(self.games_path, game_dir)
            
            # Skip directories starting with "-" or "." and non-directories
            if game_dir.startswith("-") or game_dir.startswith("."):
                continue
                
            # Skip directories with "assets" in the name
            if "assets" in game_dir.lower():
                continue
            
            # Check if it's a directory and has a main.py file
            if os.path.isdir(game_path) and os.path.exists(os.path.join(game_path, "main.py")):
                try:
                    # Import the game module
                    game_info = self.load_game_info(game_dir)
                    if game_info:
                        self.games[game_dir] = game_info
                        print(f"Loaded game: {game_info.get('title', game_dir)}")
                except Exception as e:
                    print(f"Error loading game '{game_dir}': {e}")
        
        # Debug output
        print(f"Total games found: {len(self.games)}")
        print(f"Game IDs: {', '.join(self.games.keys())}")
        
        return self.games
    
    def load_game_info(self, game_dir):
        """Load game information from the game's main module"""
        # Validate game_dir to prevent directory traversal
        if not game_dir or not isinstance(game_dir, str) or ".." in game_dir or "/" in game_dir or "\\" in game_dir:
            print(f"Invalid game directory name: {game_dir}")
            return None
            
        main_path = os.path.join(self.games_path, game_dir, "main.py")
        
        # Verify the path is within the games directory (prevent directory traversal)
        real_games_path = os.path.realpath(self.games_path)
        real_main_path = os.path.realpath(main_path)
        if not real_main_path.startswith(real_games_path):
            print(f"Security error: Attempted to access file outside games directory: {main_path}")
            return None
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(f"games.{game_dir}.main", main_path)
            if spec is None:
                print(f"Failed to create spec for {main_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            
            # Execute the module in a controlled way
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"Error executing game module '{game_dir}': {e}")
                return None
            
            # Check if the module has the required attributes
            if hasattr(module, "GAME_INFO"):
                # Validate GAME_INFO is a dictionary
                if not isinstance(module.GAME_INFO, dict):
                    print(f"Invalid GAME_INFO format in {game_dir}")
                    return None
                    
                game_info = module.GAME_INFO.copy()  # Create a copy to avoid modifying the original
                game_info["module"] = module
                game_info["directory"] = game_dir
                return game_info
            else:
                # Create default game info
                return {
                    "title": game_dir.replace("_", " ").title(),
                    "description": "No description available",
                    "author": "Unknown",
                    "version": "1.0",
                    "module": module,
                    "directory": game_dir
                }
                
        except Exception as e:
            print(f"Error importing game '{game_dir}': {e}")
            return None
    
    def launch_game(self, game_id):
        """Launch a game by its ID (directory name)"""
        if not self.games or game_id not in self.games:
            print(f"Game '{game_id}' not found")
            return None
            
        game_info = self.games[game_id]
        module = game_info.get("module")
        
        if not module:
            print(f"Module for game '{game_id}' is missing")
            return None
        
        try:
            if hasattr(module, "Game"):
                game = module.Game()
                return game
            else:
                print(f"Game '{game_id}' does not have a Game class")
                return None
        except Exception as e:
            print(f"Error launching game '{game_id}': {e}")
            return None