import pygame
import sys
import random
import os

# Game information dictionary
GAME_INFO = {
    "title": "UFO Invasion",
    "description": "Defend Earth from alien invaders",
    "author": "ByteBlitz Team",
    "version": "1.0"
}

class Player:
    """Player's spaceship"""
    
    def __init__(self, screen_width, screen_height):
        self.width = 50
        self.height = 40
        self.color = (0, 255, 0)  # Green
        self.speed = 7
        self.screen_width = screen_width
        
        # Position player at the bottom center of the screen
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 70
        
        # Shooting cooldown
        self.cooldown = 0
        self.cooldown_time = 10  # Frames between shots
    
    def move(self, direction):
        """Move the player left or right"""
        if direction == "LEFT":
            self.x = max(0, self.x - self.speed)
        elif direction == "RIGHT":
            self.x = min(self.screen_width - self.width, self.x + self.speed)
    
    def draw(self, screen):
        """Draw the player on the screen"""
        # Draw ship body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw ship cockpit
        pygame.draw.rect(screen, (100, 255, 100), 
                        (self.x + self.width // 4, self.y - 10, 
                         self.width // 2, 15))
    
    def can_shoot(self):
        """Check if player can shoot"""
        return self.cooldown <= 0
    
    def shoot(self):
        """Create a bullet"""
        if self.can_shoot():
            self.cooldown = self.cooldown_time
            return Bullet(self.x + self.width // 2, self.y)
        return None
    
    def update(self):
        """Update player state"""
        if self.cooldown > 0:
            self.cooldown -= 1


class Enemy:
    """Enemy UFO"""
    
    def __init__(self, x, y):
        self.width = 40
        self.height = 20
        self.color = (255, 0, 0)  # Red
        self.x = x
        self.y = y
        self.speed = random.randint(1, 3)
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self, screen_width):
        """Move the enemy"""
        self.x += self.speed * self.direction
        
        # Change direction if hitting screen edge
        if self.x <= 0 or self.x + self.width >= screen_width:
            self.direction *= -1
            self.y += 20  # Move down when changing direction
    
    def draw(self, screen):
        """Draw the enemy on the screen"""
        # Draw UFO body
        pygame.draw.ellipse(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
        
        # Draw UFO dome
        pygame.draw.ellipse(screen, (200, 200, 200), 
                           (self.x + self.width // 4, self.y - 10, 
                            self.width // 2, 15))
    
    def get_rect(self):
        """Get the enemy's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    """Player's bullet"""
    
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.color = (255, 255, 0)  # Yellow
        self.x = x - self.width // 2  # Center on player
        self.y = y
        self.speed = 10
    
    def move(self):
        """Move the bullet upward"""
        self.y -= self.speed
    
    def draw(self, screen):
        """Draw the bullet on the screen"""
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        """Check if bullet is off the top of the screen"""
        return self.y < -self.height
    
    def get_rect(self):
        """Get the bullet's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    """UFO Invasion game implementation"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.bg_color = (0, 0, 40)  # Dark blue
        self.score = 0
        self.level = 1
        self.lives = 3
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
        self.sound_dir = os.path.join("games", "ufo_invasion", "assets", "sounds")
        self.sounds = {}
        
        # Initialize game objects
        self.player = Player(self.width, self.height)
        self.enemies = []
        self.bullets = []
        self.clock = pygame.time.Clock()
        
        # Create enemies for the first level
        self.create_enemies(self.level)
    
    def create_enemies(self, level):
        """Create enemies for the current level"""
        self.enemies = []
        
        # Number of rows and columns based on level
        rows = min(2 + level // 2, 5)
        cols = min(5 + level, 10)
        
        # Enemy spacing
        enemy_width = 40
        enemy_height = 20
        x_margin = 20
        y_margin = 40
        
        # Create the enemies
        for row in range(rows):
            for col in range(cols):
                x = col * (enemy_width + x_margin) + x_margin
                y = row * (enemy_height + y_margin) + y_margin + 50
                
                self.enemies.append(Enemy(x, y))
    
    def start(self):
        """Start the game and return the final score"""
        # Reset game state
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.paused = False
        
        # Create the first level
        self.create_enemies(self.level)
        
        # Reset player
        self.player = Player(self.width, self.height)
        self.bullets = []
        
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
                    elif event.key == pygame.K_SPACE and not self.paused and not self.game_over:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)
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
        
        # Move player
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move("LEFT")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move("RIGHT")
        
        # Update player
        self.player.update()
        
        # Move enemies
        for enemy in self.enemies:
            enemy.move(self.width)
            
            # Check if enemy reached bottom
            if enemy.y + enemy.height >= self.player.y:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
        
        # Move bullets and check for collisions
        for bullet in self.bullets[:]:
            bullet.move()
            
            # Remove bullet if off screen
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
            
            # Check for collision with enemies
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.score += 10
                    break
        
        # Check if all enemies are destroyed
        if not self.enemies:
            self.level += 1
            self.create_enemies(self.level)
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw stars in background
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 1)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (self.width - lives_text.get_width() - 10, 10))
        
        # Draw level
        level_text = self.font_medium.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (self.width // 2 - level_text.get_width() // 2, 10))
        
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