import pygame
import sys
import os
import json
from core.gui_manager import GUIManager
from core.game_loader import GameLoader
from core.user_profile import UserProfile
from core.leaderboard import Leaderboard

class ArcadeHub:
    """Main arcade hub application"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Set up display
        self.width = self.settings["display"]["width"]
        self.height = self.settings["display"]["height"]
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("ByteBlitz Arcade")
        
        # Initialize components
        self.gui = GUIManager(self.screen, self.settings)
        self.user_profile = UserProfile(self.settings)
        self.leaderboard = Leaderboard(self.gui, self.user_profile)
        self.game_loader = GameLoader()
        
        # Load games
        self.games = self.game_loader.discover_games() or {}
        
        # State variables
        self.current_screen = "main_menu"
        self.selected_game = None
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Input handling
        self.editing_name = False
        self.player_name = self.settings["player"]["name"]
        
        # Debug flag
        self.debug = True  # Start with debug on to see any issues
        
    def load_settings(self):
        """Load settings from config file"""
        config_path = os.path.join("config", "settings.json")
        try:
            # Ensure the config directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    # Validate settings structure
                    if not isinstance(settings, dict):
                        raise ValueError("Invalid settings format")
                    return settings
            else:
                # Create default settings if file doesn't exist
                default_settings = {
                    "player": {"name": "Player1"},
                    "audio": {"music_volume": 0.7, "sfx_volume": 0.8},
                    "display": {"width": 800, "height": 600, "theme": "neon"},
                    "gameplay": {"difficulty": "normal"}
                }
                with open(config_path, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Error loading settings: {e}")
            # Return default settings
            return {
                "player": {"name": "Player1"},
                "audio": {"music_volume": 0.7, "sfx_volume": 0.8},
                "display": {"width": 800, "height": 600, "theme": "neon"},
                "gameplay": {"difficulty": "normal"}
            }
    
    def save_settings(self):
        """Save settings to config file"""
        config_path = os.path.join("config", "settings.json")
        try:
            # Ensure the config directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Create a temporary file first, then rename to avoid corruption
            temp_path = config_path + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk
                
            # Rename the temporary file to the actual settings file
            os.replace(temp_path, config_path)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize with bounds checking
                width, height = event.size
                # Enforce minimum window size
                width = max(width, 640)
                height = max(height, 480)
                # Enforce maximum window size (optional)
                width = min(width, 1920)
                height = min(height, 1080)
                
                self.width, self.height = width, height
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.settings["display"]["width"] = self.width
                self.settings["display"]["height"] = self.height
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen == "main_menu":
                        self.running = False
                    else:
                        self.current_screen = "main_menu"
                        self.editing_name = False
                elif event.key == pygame.K_F1:
                    # Toggle debug mode
                    self.debug = not self.debug
                elif event.key == pygame.K_F5:
                    # Reload games
                    print("Reloading games...")
                    self.games = self.game_loader.discover_games() or {}
                
                # Handle name editing with input sanitization
                if self.editing_name:
                    if event.key == pygame.K_RETURN:
                        # Ensure name is not empty
                        if self.player_name.strip():
                            self.settings["player"]["name"] = self.player_name
                            self.editing_name = False
                        else:
                            self.player_name = "Player1"  # Default name if empty
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    # Only allow alphanumeric characters and limit length
                    elif len(self.player_name) < 12 and event.unicode.isalnum():
                        self.player_name += event.unicode
            
            # Handle mouse clicks for settings
            elif event.type == pygame.MOUSEBUTTONDOWN and self.current_screen == "settings":
                mouse_pos = pygame.mouse.get_pos()
                
                # Check volume bar clicks
                vol_x = self.width // 2 - 250 + 300
                vol_width = 150
                
                # Music volume
                music_vol_rect = pygame.Rect(vol_x, self.height // 2 - 140, vol_width, 20)
                if music_vol_rect.collidepoint(mouse_pos):
                    self.settings["audio"]["music_volume"] = (mouse_pos[0] - vol_x) / vol_width
                    self.settings["audio"]["music_volume"] = max(0, min(1, self.settings["audio"]["music_volume"]))
                
                # SFX volume
                sfx_vol_rect = pygame.Rect(vol_x, self.height // 2 - 80, vol_width, 20)
                if sfx_vol_rect.collidepoint(mouse_pos):
                    self.settings["audio"]["sfx_volume"] = (mouse_pos[0] - vol_x) / vol_width
                    self.settings["audio"]["sfx_volume"] = max(0, min(1, self.settings["audio"]["sfx_volume"]))
                
                # Difficulty settings
                diff_options = ["easy", "normal", "hard"]
                for i, diff in enumerate(diff_options):
                    diff_x = vol_x + i * 60
                    diff_y = self.height // 2 - 20
                    diff_rect = pygame.Rect(diff_x, diff_y - 20, 40, 40)
                    if diff_rect.collidepoint(mouse_pos):
                        self.settings["gameplay"]["difficulty"] = diff
    
    def update(self):
        """Update game state"""
        self.gui.update()  # Update GUI animations
    
    def render(self):
        """Render the current screen"""
        # Draw background
        self.gui.draw_background()
        
        # Render current screen
        if self.current_screen == "main_menu":
            self.render_main_menu()
        elif self.current_screen == "game_select":
            self.render_game_select()
        elif self.current_screen == "leaderboard":
            self.render_leaderboard_screen()
        elif self.current_screen == "settings":
            self.render_settings_screen()
        
        # Draw particles
        self.gui.draw_particles()
        
        # Draw debug info if enabled
        if self.debug:
            self.gui.draw_text(f"Current Screen: {self.current_screen}", "small", "neon_green", 
                              10, 10, align="left")
            self.gui.draw_text(f"FPS: {int(self.clock.get_fps())}", "small", "neon_green", 
                              10, 30, align="left")
            self.gui.draw_text(f"Games Loaded: {len(self.games)}", "small", "neon_green", 
                              10, 50, align="left")
            if self.games:
                game_ids = ", ".join(list(self.games.keys())[:3])
                if len(self.games) > 3:
                    game_ids += "..."
                self.gui.draw_text(f"Game IDs: {game_ids}", "small", "neon_green", 
                                  10, 70, align="left")
            
            # Help text
            self.gui.draw_text("F1: Toggle Debug | F5: Reload Games", "small", "neon_yellow", 
                              self.width - 10, 10, align="right")
        
        # Update display
        pygame.display.flip()
    
    def render_main_menu(self):
        """Render the main menu screen"""
        # Draw title with arcade effect
        self.gui.draw_title("BYTEBLITZ ARCADE", self.width // 2, self.height * 0.15)
        
        # Draw decorative elements
        pygame.draw.rect(self.screen, self.gui.colors["neon_blue"], 
                        (self.width // 2 - self.width * 0.2, self.height * 0.22, 
                         self.width * 0.4, 4), border_radius=2)
        pygame.draw.rect(self.screen, self.gui.colors["neon_pink"], 
                        (self.width // 2 - self.width * 0.15, self.height * 0.24, 
                         self.width * 0.3, 2), border_radius=1)
        
        # Draw buttons - responsive sizing
        button_width = min(300, self.width * 0.4)
        button_height = min(60, self.height * 0.08)
        button_x = self.width // 2
        button_spacing = self.height * 0.12
        start_y = self.height * 0.35
        
        # Play button
        if self.gui.draw_button("PLAY GAMES", "heading", button_x, start_y, 
                               button_width, button_height, self.gui.colors["neon_green"])[0]:
            if self.games:
                self.current_screen = "game_select"
            else:
                print("No games available to play")
        
        # Leaderboard button
        if self.gui.draw_button("LEADERBOARD", "heading", button_x, start_y + button_spacing, 
                               button_width, button_height, self.gui.colors["neon_blue"])[0]:
            self.current_screen = "leaderboard"
        
        # Settings button
        if self.gui.draw_button("SETTINGS", "heading", button_x, start_y + button_spacing * 2, 
                               button_width, button_height, self.gui.colors["neon_yellow"])[0]:
            self.current_screen = "settings"
        
        # Quit button
        if self.gui.draw_button("QUIT", "heading", button_x, start_y + button_spacing * 3, 
                               button_width, button_height, self.gui.colors["neon_pink"])[0]:
            self.running = False
        
        # Draw player info in a panel
        info_panel = self.gui.draw_panel(10, self.height - 50, 200, 40, alpha=180)
        self.gui.draw_text(f"PLAYER: {self.settings['player']['name']}", "small", 
                          "light_text", info_panel.centerx, info_panel.centery)
        
        # Draw version info
        self.gui.draw_text("v1.0", "small", "light_text", 
                          self.width - 20, self.height - 20, align="right")
    
    def render_game_select(self):
        """Render the game selection screen"""
        # Draw header with panel
        header_height = self.height * 0.1
        header_panel = self.gui.draw_panel(0, 0, self.width, header_height)
        self.gui.draw_text("SELECT GAME", "heading", "neon_green", 
                          self.width // 2, header_height // 2, glow=True)
        
        # Draw game list
        if not self.games:
            self.gui.draw_text("NO GAMES FOUND!", "heading", "neon_pink", 
                              self.width // 2, self.height // 2, glow=True)
            self.gui.draw_text("Press F5 to reload games", "normal", "neon_yellow", 
                              self.width // 2, self.height // 2 + 40)
            
            # Back button at the bottom of the screen
            back_button_width = min(150, self.width * 0.2)
            back_button_height = min(40, self.height * 0.06)
            if self.gui.draw_button("BACK", "normal", self.width // 2, self.height - 40, 
                                   back_button_width, back_button_height, self.gui.colors["neon_pink"])[0]:
                self.current_screen = "main_menu"
            return
        
        # Draw game selection panel - responsive sizing
        panel_width = min(500, self.width * 0.8)
        panel_height = self.height * 0.75
        panel_x = self.width // 2 - panel_width // 2
        panel_y = self.height * 0.15
        
        games_panel = self.gui.draw_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Draw instruction text at the top of the panel
        self.gui.draw_text("CHOOSE A GAME", "heading", "neon_yellow", 
                          self.width // 2, panel_y + 30, glow=True)
        
        # Draw game buttons with proper alignment - smaller buttons
        button_width = min(300, panel_width * 0.8)
        button_height = min(50, panel_height * 0.1)
        button_x = self.width // 2
        start_y = panel_y + 70
        button_spacing = min(80, panel_height * 0.15)
        
        # Calculate max visible games based on panel height
        max_visible_games = min(len(self.games), int((panel_height - 120) / button_spacing))
        
        # Draw each game button
        game_items = list(self.games.items())
        for i in range(min(len(game_items), max_visible_games)):
            game_id, game_info = game_items[i]
            game_title = game_info.get("title", game_id.replace("_", " ").title())
            
            # Get high score
            high_score = self.user_profile.get_high_score(game_id)
            
            # Draw game button with consistent styling
            button_y = start_y + (i * button_spacing)
            
            # Draw game button - use heading font for better visibility
            if self.gui.draw_button(game_title.upper(), "heading", button_x, button_y, 
                                   button_width, button_height, self.gui.colors["neon_blue"])[0]:
                self.launch_game(game_id)
            
            # Draw high score with better alignment (below the button)
            score_text = f"HIGH SCORE: {high_score}"
            self.gui.draw_text(score_text, "normal", "neon_yellow", 
                              button_x, button_y + button_height//2 + 15, shadow=True)
        
        # Back button at the bottom of the screen
        back_button_width = min(150, self.width * 0.2)
        back_button_height = min(40, self.height * 0.06)
        if self.gui.draw_button("BACK", "normal", self.width // 2, self.height - 40, 
                               back_button_width, back_button_height, self.gui.colors["neon_pink"])[0]:
            self.current_screen = "main_menu"
    
    def render_leaderboard_screen(self):
        """Render the leaderboard screen"""
        # Draw header with panel - responsive
        header_height = self.height * 0.1
        header_panel = self.gui.draw_panel(0, 0, self.width, header_height)
        self.gui.draw_text("LEADERBOARDS", "heading", "neon_blue", 
                          self.width // 2, header_height // 2, glow=True)
        
        # Draw game selection for leaderboard
        if not self.games:
            self.gui.draw_text("NO GAMES FOUND!", "heading", "neon_pink", 
                              self.width // 2, self.height // 2, glow=True)
            self.gui.draw_text("Press F5 to reload games", "normal", "neon_yellow", 
                              self.width // 2, self.height // 2 + 40)
        else:
            # Draw game selection panel - responsive
            games_panel_width = self.width * 0.25
            games_panel = self.gui.draw_panel(20, self.height * 0.15, 
                                             games_panel_width, self.height * 0.75)
            self.gui.draw_text("GAMES", "heading", "neon_yellow", 
                              games_panel.centerx, self.height * 0.18)
            
            # Draw game buttons - responsive
            button_width = games_panel_width * 0.8
            button_height = min(40, self.height * 0.06)
            button_x = games_panel.centerx
            start_y = self.height * 0.22
            button_spacing = self.height * 0.08
            
            # Calculate max visible games
            max_visible_games = min(len(self.games), int((self.height * 0.65) / button_spacing))
            
            game_items = list(self.games.items())
            for i in range(min(len(game_items), max_visible_games)):
                game_id, game_info = game_items[i]
                game_title = game_info.get("title", game_id.replace("_", " ").title())
                
                # Highlight selected game
                color = self.gui.colors["neon_green"] if self.selected_game == game_id else self.gui.colors["neon_blue"]
                
                if self.gui.draw_button(game_title.upper(), "normal", button_x, start_y + (i * button_spacing), 
                                       button_width, button_height, color)[0]:
                    self.selected_game = game_id
            
            # Display leaderboard for selected game - responsive
            if self.selected_game:
                leaderboard_x = games_panel_width + 50
                leaderboard_width = self.width - leaderboard_x - 20
                self.leaderboard.display(self.selected_game, 
                                        leaderboard_x, self.height * 0.15, 
                                        leaderboard_width, self.height * 0.75)
            else:
                # Show instruction if no game is selected
                self.gui.draw_text("Select a game to view leaderboard", "normal", "light_text", 
                                  self.width * 0.6, self.height // 2)
        
        # Back button - responsive
        back_button_width = min(150, self.width * 0.15)
        back_button_height = min(40, self.height * 0.06)
        if self.gui.draw_button("BACK", "normal", back_button_width // 2 + 20, self.height - 40, 
                               back_button_width, back_button_height, self.gui.colors["neon_pink"])[0]:
            self.current_screen = "main_menu"
    
    def render_settings_screen(self):
        """Render the settings screen"""
        # Draw header with panel - responsive
        header_height = self.height * 0.1
        header_panel = self.gui.draw_panel(0, 0, self.width, header_height)
        self.gui.draw_text("SETTINGS", "heading", "neon_yellow", 
                          self.width // 2, header_height // 2, glow=True)
        
        # Draw settings panel - responsive
        panel_width = min(500, self.width * 0.8)
        panel_height = self.height * 0.7
        panel_x = self.width // 2 - panel_width // 2
        panel_y = self.height * 0.15
        
        settings_panel = self.gui.draw_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Draw settings title
        self.gui.draw_text("GAME OPTIONS", "heading", "neon_green", 
                          panel_x + panel_width // 2, panel_y + panel_height * 0.08)
        
        # Draw settings divider
        pygame.draw.line(self.screen, self.gui.colors["neon_blue"], 
                        (panel_x + panel_width * 0.1, panel_y + panel_height * 0.15), 
                        (panel_x + panel_width * 0.9, panel_y + panel_height * 0.15), 2)
        
        # Calculate positions based on panel size
        label_x = panel_x + panel_width * 0.3
        input_x = panel_x + panel_width * 0.7
        row1_y = panel_y + panel_height * 0.25
        row2_y = panel_y + panel_height * 0.4
        row3_y = panel_y + panel_height * 0.55
        
        # Player name setting
        self.gui.draw_text("PLAYER NAME:", "heading", "neon_green", 
                          label_x, row1_y, align="left")
        
        # Player name input field
        name_panel = self.gui.draw_panel(input_x - 75, row1_y - 15, 150, 30, alpha=150)
        
        # Show editing state
        if self.editing_name:
            name_text = self.player_name + "_"
            pygame.draw.rect(self.screen, self.gui.colors["neon_pink"], 
                            name_panel.inflate(4, 4), 2, border_radius=3)
        else:
            name_text = self.settings['player']['name']
            
            # Make name field clickable
            mouse_pos = pygame.mouse.get_pos()
            if name_panel.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.editing_name = True
                self.player_name = self.settings['player']['name']
        
        self.gui.draw_text(name_text, "heading", "light_text", 
                          name_panel.centerx, name_panel.centery)
        
        # Volume settings
        self.gui.draw_text("MUSIC VOLUME:", "heading", "neon_green", 
                          label_x, row2_y, align="left")
        
        # Draw volume bar (interactive)
        vol_x = input_x - 75
        vol_y = row2_y
        vol_width = 150
        vol_height = 20
        
        # Background bar
        pygame.draw.rect(self.screen, self.gui.colors["dark_bg"], 
                        (vol_x, vol_y - vol_height//2, vol_width, vol_height))
        
        # Value bar
        music_vol = self.settings["audio"]["music_volume"]
        pygame.draw.rect(self.screen, self.gui.colors["neon_blue"], 
                        (vol_x, vol_y - vol_height//2, 
                         int(vol_width * music_vol), vol_height))
        
        # Volume knob
        knob_x = vol_x + int(vol_width * music_vol)
        pygame.draw.circle(self.screen, self.gui.colors["light_text"], 
                          (knob_x, vol_y), 10)
        
        # Sound effects volume
        self.gui.draw_text("SFX VOLUME:", "heading", "neon_green", 
                          label_x, row3_y, align="left")
        
        # Draw SFX volume bar (interactive)
        sfx_y = row3_y
        
        # Background bar
        pygame.draw.rect(self.screen, self.gui.colors["dark_bg"], 
                        (vol_x, sfx_y - vol_height//2, vol_width, vol_height))
        
        # Value bar
        sfx_vol = self.settings["audio"]["sfx_volume"]
        pygame.draw.rect(self.screen, self.gui.colors["neon_green"], 
                        (vol_x, sfx_y - vol_height//2, 
                         int(vol_width * sfx_vol), vol_height))
        
        # Volume knob
        knob_x = vol_x + int(vol_width * sfx_vol)
        pygame.draw.circle(self.screen, self.gui.colors["light_text"], 
                          (knob_x, sfx_y), 10)
        
        # Difficulty setting
        diff_y = panel_y + panel_height * 0.7
        self.gui.draw_text("DIFFICULTY:", "heading", "neon_green", 
                          label_x, diff_y, align="left")
        
        # Draw difficulty options (interactive)
        diff_options = ["easy", "normal", "hard"]
        diff_colors = [self.gui.colors["neon_green"], 
                      self.gui.colors["neon_yellow"], 
                      self.gui.colors["neon_pink"]]
        
        diff_spacing = min(60, panel_width * 0.12)
        for i, diff in enumerate(diff_options):
            diff_x = vol_x + i * diff_spacing
            diff_size = min(40, panel_width * 0.08)
            
            # Draw difficulty button
            diff_rect = pygame.Rect(diff_x, diff_y - diff_size//2, diff_size, diff_size)
            color = diff_colors[i]
            
            # Highlight selected difficulty
            if diff == self.settings["gameplay"]["difficulty"]:
                pygame.draw.rect(self.screen, color, diff_rect, border_radius=5)
                pygame.draw.rect(self.screen, (255, 255, 255), diff_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(self.screen, color, diff_rect, 1, border_radius=5)
            
            # Draw first letter of difficulty
            self.gui.draw_text(diff[0].upper(), "heading", "light_text", 
                              diff_rect.centerx, diff_rect.centery)
        
        # Save button - responsive
        save_button_width = min(150, panel_width * 0.3)
        save_button_height = min(40, panel_height * 0.1)
        if self.gui.draw_button("SAVE", "heading", panel_x + panel_width // 2, 
                               panel_y + panel_height * 0.85, 
                               save_button_width, save_button_height, 
                               self.gui.colors["neon_green"])[0]:
            self.save_settings()
            self.current_screen = "main_menu"
        
        # Back button - responsive
        back_button_width = min(150, self.width * 0.15)
        back_button_height = min(40, self.height * 0.06)
        if self.gui.draw_button("BACK", "heading", back_button_width // 2 + 20, self.height - 40, 
                               back_button_width, back_button_height, 
                               self.gui.colors["neon_pink"])[0]:
            self.current_screen = "main_menu"
    
    def launch_game(self, game_id):
        """Launch a selected game"""
        if self.debug:
            print(f"Launching game: {game_id}")
            
        game = self.game_loader.launch_game(game_id)
        
        if game:
            # Run the game
            try:
                score = game.start()
                
                # Update score if game returned a score
                if isinstance(score, (int, float)) and score > 0:
                    self.leaderboard.update_score(game_id, score)
                    
            except Exception as e:
                print(f"Error launching game '{game_id}': {e}")
            
            # Always return to game select screen after playing
            self.current_screen = "game_select"
        else:
            print(f"Failed to launch game: {game_id}")

if __name__ == "__main__":
    arcade = ArcadeHub()
    arcade.run()