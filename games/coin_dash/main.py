import pygame
import sys
import random
import os

# Game information dictionary
GAME_INFO = {
    "title": "Coin Dash",
    "description": "Collect coins while avoiding obstacles",
    "author": "ByteBlitz Team",
    "version": "1.0"
}

class Player:
    """Player character"""
    
    def __init__(self, screen_width, screen_height):
        self.width = 30
        self.height = 30
        self.color = (0, 200, 255)  # Cyan
        self.speed = 5
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Position player at the center of the screen
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height // 2 - self.height // 2
    
    def move(self, dx, dy):
        """Move the player"""
        # Update position with bounds checking
        self.x = max(0, min(self.screen_width - self.width, self.x + dx))
        self.y = max(0, min(self.screen_height - self.height, self.y + dy))
    
    def draw(self, screen):
        """Draw the player on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw face details
        eye_size = 5
        pygame.draw.circle(screen, (0, 0, 0), 
                          (self.x + 10, self.y + 10), eye_size)
        pygame.draw.circle(screen, (0, 0, 0), 
                          (self.x + 20, self.y + 10), eye_size)
        
        # Draw smile
        pygame.draw.arc(screen, (0, 0, 0),
                       (self.x + 5, self.y + 10, 20, 15),
                       0.2, 2.9, 2)
    
    def get_rect(self):
        """Get the player's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Coin:
    """Collectible coin"""
    
    def __init__(self, screen_width, screen_height):
        self.radius = 10
        self.color = (255, 215, 0)  # Gold
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn()
    
    def spawn(self):
        """Spawn the coin at a random position"""
        margin = self.radius * 2
        self.x = random.randint(margin, self.screen_width - margin)
        self.y = random.randint(margin, self.screen_height - margin)
    
    def draw(self, screen):
        """Draw the coin on the screen"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
        # Draw inner circle for 3D effect
        pygame.draw.circle(screen, (255, 255, 150), 
                          (self.x, self.y), self.radius - 3)
    
    def get_rect(self):
        """Get the coin's rectangle for collision detection"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class Obstacle:
    """Moving obstacle"""
    
    def __init__(self, screen_width, screen_height):
        self.width = random.randint(20, 40)
        self.height = random.randint(20, 40)
        self.color = (255, 0, 0)  # Red
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Random position at the edge of the screen
        edge = random.choice(["top", "right", "bottom", "left"])
        if edge == "top":
            self.x = random.randint(0, screen_width - self.width)
            self.y = -self.height
            self.dx = random.choice([-1, 0, 1])
            self.dy = random.randint(1, 3)
        elif edge == "right":
            self.x = screen_width
            self.y = random.randint(0, screen_height - self.height)
            self.dx = random.randint(-3, -1)
            self.dy = random.choice([-1, 0, 1])
        elif edge == "bottom":
            self.x = random.randint(0, screen_width - self.width)
            self.y = screen_height
            self.dx = random.choice([-1, 0, 1])
            self.dy = random.randint(-3, -1)
        else:  # left
            self.x = -self.width
            self.y = random.randint(0, screen_height - self.height)
            self.dx = random.randint(1, 3)
            self.dy = random.choice([-1, 0, 1])
    
    def move(self):
        """Move the obstacle"""
        self.x += self.dx
        self.y += self.dy
    
    def draw(self, screen):
        """Draw the obstacle on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw spikes
        spike_length = 5
        # Top spikes
        for i in range(self.width // 10):
            pygame.draw.polygon(screen, (150, 0, 0), [
                (self.x + 5 + i * 10, self.y),
                (self.x + 10 + i * 10, self.y - spike_length),
                (self.x + 15 + i * 10, self.y)
            ])
        
        # Bottom spikes
        for i in range(self.width // 10):
            pygame.draw.polygon(screen, (150, 0, 0), [
                (self.x + 5 + i * 10, self.y + self.height),
                (self.x + 10 + i * 10, self.y + self.height + spike_length),
                (self.x + 15 + i * 10, self.y + self.height)
            ])
    
    def is_off_screen(self):
        """Check if the obstacle is completely off the screen"""
        return (self.x + self.width < 0 or
                self.x > self.screen_width or
                self.y + self.height < 0 or
                self.y > self.screen_height)
    
    def get_rect(self):
        """Get the obstacle's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    """Coin Dash game implementation"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.bg_color = (100, 100, 200)  # Light blue
        self.score = 0
        self.time_left = 30  # Game time in seconds
        self.game_over = False
        self.paused = False
        
        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()
            
        # Set up display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GAME_INFO["title"])
        
        # Load fonts
        self.font_dir = os.path.join("assets", "fonts")
        try:
            self.font_large = pygame.font.Font(os.path.join(self.font_dir, "arcade.ttf"), 36)
            self.font_medium = pygame.font.Font(os.path.join(self.font_dir, "arcade.ttf"), 24)
            self.font_small = pygame.font.Font(os.path.join(self.font_dir, "arcade.ttf"), 18)
        except FileNotFoundError:
            self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_medium = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 18)
        
        # Load sounds
        self.sound_dir = os.path.join("games", "coin_dash", "assets", "sounds")
        self.sounds = {}
        
        # Initialize game objects
        self.player = Player(self.width, self.height)
        self.coins = []
        self.obstacles = []
        self.clock = pygame.time.Clock()
        
        # Create initial coins
        for _ in range(5):
            self.coins.append(Coin(self.width, self.height))
        
        # Timer for obstacle spawning
        self.obstacle_timer = 0
        self.obstacle_spawn_time = 60  # Frames between obstacle spawns
        
        # Timer for game countdown
        self.timer = 0
    
    def start(self):
        """Start the game and return the final score"""
        # Reset game state
        self.score = 0
        self.time_left = 30
        self.game_over = False
        self.paused = False
        
        # Reset game objects
        self.player = Player(self.width, self.height)
        self.coins = []
        self.obstacles = []
        
        # Create initial coins
        for _ in range(5):
            self.coins.append(Coin(self.width, self.height))
        
        # Reset timers
        self.obstacle_timer = 0
        self.timer = 0
        
        # Main game loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.score
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.score
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.game_over:
                        return self.start()  # Restart game
            
            # Update game state if not paused or game over
            if not self.paused and not self.game_over:
                self.update()
            
            # Render game
            self.render()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        return self.score
    
    def update(self):
        """Update game state"""
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Calculate movement
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.player.speed
        
        # Move player
        self.player.move(dx, dy)
        
        # Check for coin collisions
        player_rect = self.player.get_rect()
        for coin in self.coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.coins.remove(coin)
                self.score += 1
                self.time_left += 1  # Add time for each coin
                
                # Spawn a new coin
                self.coins.append(Coin(self.width, self.height))
        
        # Move obstacles
        for obstacle in self.obstacles[:]:
            obstacle.move()
            
            # Remove obstacles that are off screen
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
            
            # Check for collision with player
            elif player_rect.colliderect(obstacle.get_rect()):
                self.game_over = True
        
        # Spawn new obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer >= self.obstacle_spawn_time:
            self.obstacles.append(Obstacle(self.width, self.height))
            self.obstacle_timer = 0
            
            # Decrease spawn time as game progresses
            self.obstacle_spawn_time = max(30, self.obstacle_spawn_time - 1)
        
        # Update timer
        self.timer += 1
        if self.timer >= 60:  # 60 frames = 1 second at 60 FPS
            self.time_left -= 1
            self.timer = 0
            
            # Check if time is up
            if self.time_left <= 0:
                self.game_over = True
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw time left
        time_text = self.font_medium.render(f"Time: {self.time_left}", True, (255, 255, 255))
        self.screen.blit(time_text, (self.width - time_text.get_width() - 10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.font_medium.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            
            self.screen.blit(game_over_text, 
                            (self.width // 2 - game_over_text.get_width() // 2, 
                             self.height // 2 - game_over_text.get_height() // 2))
            self.screen.blit(restart_text, 
                            (self.width // 2 - restart_text.get_width() // 2, 
                             self.height // 2 + 50))
        
        # Draw pause message
        elif self.paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, 
                            (self.width // 2 - pause_text.get_width() // 2, 
                             self.height // 2 - pause_text.get_height() // 2))
        
        # Update display
        pygame.display.flip()
    
    def quit(self):
        """Clean up resources"""
        pass  # Nothing to clean up

# For testing the game directly
if __name__ == "__main__":
    game = Game()
    final_score = game.start()
    print(f"Final score: {final_score}")
    pygame.quit()
    sys.exit()