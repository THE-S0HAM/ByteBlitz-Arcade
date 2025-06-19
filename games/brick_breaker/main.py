import pygame
import sys
import random
import os

# Game information dictionary
GAME_INFO = {
    "title": "Brick Breaker",
    "description": "Break all the bricks with a bouncing ball",
    "author": "ByteBlitz Team",
    "version": "1.0"
}

class Paddle:
    """Player-controlled paddle"""
    
    def __init__(self, screen_width, screen_height):
        self.width = 100
        self.height = 20
        self.color = (0, 150, 255)  # Blue
        self.speed = 8
        self.screen_width = screen_width
        
        # Position paddle at the bottom center of the screen
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 50
    
    def move(self, direction):
        """Move the paddle left or right"""
        if direction == "LEFT":
            self.x = max(0, self.x - self.speed)
        elif direction == "RIGHT":
            self.x = min(self.screen_width - self.width, self.x + self.speed)
    
    def draw(self, screen):
        """Draw the paddle on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add a highlight effect
        pygame.draw.rect(screen, (100, 200, 255), (self.x, self.y, self.width, 5))
    
    def get_rect(self):
        """Get the paddle's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    """Bouncing ball"""
    
    def __init__(self, screen_width, screen_height):
        self.radius = 10
        self.color = (255, 255, 255)  # White
        self.speed_x = 5
        self.speed_y = -5
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Position ball at the center of the screen
        self.x = screen_width // 2
        self.y = screen_height // 2
        
        # Ball is initially not moving
        self.moving = False
    
    def move(self):
        """Move the ball if it's in motion"""
        if not self.moving:
            return
            
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x <= self.radius or self.x >= self.screen_width - self.radius:
            self.speed_x = -self.speed_x
        if self.y <= self.radius:
            self.speed_y = -self.speed_y
    
    def draw(self, screen):
        """Draw the ball on the screen"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def reset(self, paddle):
        """Reset the ball to the paddle position"""
        self.x = paddle.x + paddle.width // 2
        self.y = paddle.y - self.radius
        self.moving = False
        self.speed_x = random.choice([-5, 5])
        self.speed_y = -5
    
    def launch(self):
        """Start the ball moving"""
        if not self.moving:
            self.moving = True
    
    def check_paddle_collision(self, paddle):
        """Check for collision with the paddle"""
        paddle_rect = paddle.get_rect()
        
        if (self.y + self.radius >= paddle_rect.top and 
            self.y - self.radius <= paddle_rect.bottom and
            self.x + self.radius >= paddle_rect.left and
            self.x - self.radius <= paddle_rect.right):
            
            # Calculate bounce angle based on where the ball hit the paddle
            relative_x = (self.x - (paddle_rect.left + paddle_rect.width / 2)) / (paddle_rect.width / 2)
            self.speed_x = relative_x * 7  # Adjust horizontal speed based on hit position
            self.speed_y = -abs(self.speed_y)  # Always bounce up
            return True
            
        return False
    
    def check_brick_collision(self, bricks):
        """Check for collision with bricks and return score earned"""
        score = 0
        
        for brick in bricks[:]:
            brick_rect = brick.get_rect()
            
            if (self.y + self.radius >= brick_rect.top and 
                self.y - self.radius <= brick_rect.bottom and
                self.x + self.radius >= brick_rect.left and
                self.x - self.radius <= brick_rect.right):
                
                # Determine which side of the brick was hit
                # Calculate distances to each edge
                dist_left = abs(self.x - brick_rect.left)
                dist_right = abs(self.x - brick_rect.right)
                dist_top = abs(self.y - brick_rect.top)
                dist_bottom = abs(self.y - brick_rect.bottom)
                
                # Find the minimum distance
                min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                
                # Bounce based on which side was hit
                if min_dist == dist_left or min_dist == dist_right:
                    self.speed_x = -self.speed_x
                else:
                    self.speed_y = -self.speed_y
                
                # Remove the brick and add score
                bricks.remove(brick)
                score += brick.points
                break
                
        return score
    
    def is_out_of_bounds(self):
        """Check if the ball is below the bottom of the screen"""
        return self.y > self.screen_height + self.radius


class Brick:
    """Breakable brick"""
    
    def __init__(self, x, y, width, height, color, points):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.points = points
    
    def draw(self, screen):
        """Draw the brick on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add a highlight effect
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, 2))
    
    def get_rect(self):
        """Get the brick's rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    """Brick Breaker game implementation"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.bg_color = (0, 0, 30)  # Dark blue
        self.score = 0
        self.lives = 3
        self.level = 1
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
        self.sound_dir = os.path.join("games", "brick_breaker", "assets", "sounds")
        self.sounds = {}
        
        # Initialize game objects
        self.paddle = Paddle(self.width, self.height)
        self.ball = Ball(self.width, self.height)
        self.bricks = []
        self.clock = pygame.time.Clock()
        
        # Create bricks for the first level
        self.create_level(self.level)
    
    def create_level(self, level):
        """Create bricks for the current level"""
        self.bricks = []
        
        # Brick properties
        brick_width = 75
        brick_height = 30
        brick_margin = 5
        top_margin = 50
        
        # Number of rows and columns
        rows = min(3 + level, 8)  # Increase rows with level, max 8
        cols = 10
        
        # Colors for different rows (points increase with row)
        colors = [
            (255, 0, 0),    # Red (1 point)
            (255, 165, 0),  # Orange (2 points)
            (255, 255, 0),  # Yellow (3 points)
            (0, 255, 0),    # Green (4 points)
            (0, 0, 255),    # Blue (5 points)
            (75, 0, 130),   # Indigo (6 points)
            (148, 0, 211),  # Violet (7 points)
            (255, 20, 147)  # Pink (8 points)
        ]
        
        # Create the bricks
        for row in range(rows):
            for col in range(cols):
                x = col * (brick_width + brick_margin) + brick_margin
                y = row * (brick_height + brick_margin) + top_margin
                color = colors[row % len(colors)]
                points = row + 1  # Points based on row
                
                self.bricks.append(Brick(x, y, brick_width, brick_height, color, points))
    
    def start(self):
        """Start the game and return the final score"""
        # Reset game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.paused = False
        
        # Create the first level
        self.create_level(self.level)
        
        # Reset paddle and ball
        self.paddle = Paddle(self.width, self.height)
        self.ball = Ball(self.width, self.height)
        self.ball.reset(self.paddle)
        
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
                    elif event.key == pygame.K_SPACE:
                        self.ball.launch()
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
        
        # Move paddle
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move("LEFT")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move("RIGHT")
        
        # If ball is not moving, position it on the paddle
        if not self.ball.moving:
            self.ball.reset(self.paddle)
        else:
            # Move ball
            self.ball.move()
            
            # Check for paddle collision
            self.ball.check_paddle_collision(self.paddle)
            
            # Check for brick collision
            score = self.ball.check_brick_collision(self.bricks)
            self.score += score
            
            # Check if all bricks are cleared
            if not self.bricks:
                self.level += 1
                self.create_level(self.level)
                self.ball.reset(self.paddle)
            
            # Check if ball is out of bounds
            if self.ball.is_out_of_bounds():
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.ball.reset(self.paddle)
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw bricks
        for brick in self.bricks:
            brick.draw(self.screen)
        
        # Draw paddle
        self.paddle.draw(self.screen)
        
        # Draw ball
        self.ball.draw(self.screen)
        
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
        
        # Draw launch instruction if ball is not moving
        elif not self.ball.moving:
            launch_text = self.font_small.render("Press SPACE to launch", True, (255, 255, 255))
            self.screen.blit(launch_text, 
                            (self.width // 2 - launch_text.get_width() // 2, 
                             self.height - 100))
        
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