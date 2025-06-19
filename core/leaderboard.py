import pygame
from datetime import datetime

class Leaderboard:
    """Displays and manages game leaderboards"""
    
    def __init__(self, gui_manager, user_profile):
        self.gui = gui_manager
        self.user_profile = user_profile
        self.screen = gui_manager.screen
        
    def display(self, game_id, x, y, width, height):
        """Display the leaderboard for a specific game"""
        # Draw panel background
        panel_rect = self.gui.draw_panel(x, y, width, height)
        
        # Draw header
        self.gui.draw_text("LEADERBOARD", "heading", "neon_green", 
                          panel_rect.centerx, y + 30, glow=True)
        
        # Draw decorative line
        pygame.draw.line(self.screen, self.gui.colors["neon_blue"], 
                        (x + 20, y + 60), (x + width - 20, y + 60), 3)
        
        # Get high scores
        high_scores = self.user_profile.get_global_high_scores(game_id, limit=8)
        
        if not high_scores:
            self.gui.draw_text("NO SCORES YET", "heading", "neon_pink", 
                              panel_rect.centerx, panel_rect.centery, glow=True)
            return
            
        # Draw column headers with background
        header_y = y + 80
        header_height = 30
        header_bg = pygame.Rect(x + 10, header_y - header_height//2, width - 20, header_height)
        pygame.draw.rect(self.screen, self.gui.colors["neon_blue"], header_bg, border_radius=3)
        
        # Draw column headers
        col_y = header_y
        self.gui.draw_text("RANK", "normal", "light_text", x + 50, col_y, align="center")
        self.gui.draw_text("PLAYER", "normal", "light_text", x + 150, col_y, align="center")
        self.gui.draw_text("SCORE", "normal", "light_text", x + 250, col_y, align="center")
        self.gui.draw_text("DATE", "normal", "light_text", x + width - 80, col_y, align="center")
        
        # Draw scores with alternating row backgrounds
        for i, score in enumerate(high_scores):
            row_y = col_y + 40 + (i * 35)
            
            # Draw row background (alternating colors)
            row_bg = pygame.Rect(x + 10, row_y - 15, width - 20, 30)
            bg_color = (30, 30, 50) if i % 2 == 0 else (20, 20, 40)
            pygame.draw.rect(self.screen, bg_color, row_bg, border_radius=3)
            
            # Highlight current user
            text_color = "neon_blue" if score["username"] == self.user_profile.current_user else "light_text"
            
            # Format date
            date_str = "Unknown"
            if "timestamp" in score and score["timestamp"]:
                date_obj = datetime.fromtimestamp(score["timestamp"])
                date_str = date_obj.strftime("%Y-%m-%d")
            
            # Draw rank with medal for top 3
            if i < 3:
                medal_colors = [self.gui.colors["neon_yellow"], 
                               (200, 200, 200), 
                               (205, 127, 50)]  # Gold, Silver, Bronze
                pygame.draw.circle(self.screen, medal_colors[i], 
                                  (x + 50, row_y), 12)
                self.gui.draw_text(f"{i+1}", "small", "dark_bg", x + 50, row_y)
            else:
                self.gui.draw_text(f"{i+1}", "normal", text_color, x + 50, row_y)
            
            # Draw score row
            self.gui.draw_text(score["username"], "normal", text_color, x + 150, row_y)
            self.gui.draw_text(f"{score['score']}", "normal", text_color, x + 250, row_y)
            self.gui.draw_text(date_str, "small", text_color, x + width - 80, row_y)
            
    def update_score(self, game_id, score, level=1):
        """Add a new score to the leaderboard"""
        self.user_profile.add_score(game_id, score, level)
        
    def get_high_score(self, game_id):
        """Get the current user's high score for a game"""
        return self.user_profile.get_high_score(game_id)