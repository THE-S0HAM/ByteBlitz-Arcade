import pygame
import sys
import random
import os

# Game information dictionary
GAME_INFO = {
    "title": "Snake Reloaded",
    "description": "A modern take on the classic Snake game with power-ups and obstacles",
    "author": "ByteBlitz Team",
    "version": "1.0"
}

class Snake:
    """Snake player class"""
    
    def __init__(self, x, y, cell_size):
        self.cell_size = cell_size
        self.direction = "RIGHT"
        self.change_to = self.direction
        
        # Initial snake body (3 segments)
        self.body = [
            [x, y],
            [x - cell_size, y],
            [x - (2 * cell_size), y]
        ]
        
        # Colors
        self.head_color = (0, 255, 0)  # Green
        self.body_color = (0, 200, 0)  # Darker green
    
    def handle_key(self, key):
        """Handle keyboard input for direction changes"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.change_to = "UP"
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.change_to = "DOWN"
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.change_to = "LEFT"
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.change_to = "RIGHT"
    
    def move(self):
        """Move the snake based on current direction"""
        # Update direction based on user input
        # Prevent 180-degree turns
        if self.change_to == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif self.change_to == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
        elif self.change_to == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif self.change_to == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
        
        # Move the head
        head = self.body[0].copy()
        if self.direction == "UP":
            head[1] -= self.cell_size
        elif self.direction == "DOWN":
            head[1] += self.cell_size
        elif self.direction == "LEFT":
            head[0] -= self.cell_size
        elif self.direction == "RIGHT":
            head[0] += self.cell_size
        
        # Insert new head
        self.body.insert(0, head)
        
        # Remove tail (unless we're growing)
        if len(self.body) > self.length:
            self.body.pop()
    
    def grow(self):
        """Increase snake length"""
        self.length += 1
    
    def draw(self, screen):
        """Draw the snake on the screen"""
        # Draw head
        pygame.draw.rect(screen, self.head_color, 
                        (self.body[0][0], self.body[0][1], 
                         self.cell_size, self.cell_size))
        
        # Draw body
        for segment in self.body[1:]:
            pygame.draw.rect(screen, self.body_color, 
                            (segment[0], segment[1], 
                             self.cell_size, self.cell_size))
    
    def check_collision_with_food(self, food):
        """Check if snake has collided with food"""
        return self.body[0][0] == food.position[0] and self.body[0][1] == food.position[1]
    
    def check_collision_with_walls(self, width, height):
        """Check if snake has collided with walls"""
        head = self.body[0]
        return (
            head[0] < 0 or 
            head[0] >= width or 
            head[1] < 0 or 
            head[1] >= height
        )
    
    def check_collision_with_self(self):
        """Check if snake has collided with itself"""
        head = self.body[0]
        return head in self.body[1:]
    
    @property
    def length(self):
        return len(self.body)
    
    @length.setter
    def length(self, value):
        # This is used by the grow method
        pass  # The actual length is determined by the body list


class Food:
    """Food class for the snake to eat"""
    
    def __init__(self, screen_width, screen_height, cell_size):
        self.cell_size = cell_size
        self.color = (255, 0, 0)  # Red
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.position = [0, 0]
        self.respawn(screen_width, screen_height)
    
    def respawn(self, screen_width=None, screen_height=None, snake_body=None):
        """Spawn food at a random position, avoiding the snake's body"""
        if screen_width:
            self.screen_width = screen_width
        if screen_height:
            self.screen_height = screen_height
            
        # Calculate grid dimensions
        grid_width = self.screen_width // self.cell_size
        grid_height = self.screen_height // self.cell_size
        
        # Generate random position
        while True:
            x = random.randint(0, grid_width - 1) * self.cell_size
            y = random.randint(0, grid_height - 1) * self.cell_size
            
            # Check if position overlaps with snake
            if snake_body and [x, y] in snake_body:
                continue  # Try again
            
            self.position = [x, y]
            break
    
    def draw(self, screen):
        """Draw the food on the screen"""
        pygame.draw.rect(screen, self.color, 
                        (self.position[0], self.position[1], 
                         self.cell_size, self.cell_size))


class Game:
    """Snake Reloaded game implementation"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.cell_size = 20
        self.bg_color = (10, 10, 30)
        self.grid_color = (30, 30, 50)
        self.score = 0
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
        self.sound_dir = os.path.join("games", "snake_reloaded", "assets", "sounds")
        self.sounds = {}
        try:
            self.sounds["eat"] = pygame.mixer.Sound(os.path.join(self.sound_dir, "eat.wav"))
            self.sounds["crash"] = pygame.mixer.Sound(os.path.join(self.sound_dir, "crash.wav"))
        except:
            print("Could not load sounds")
        
        # Initialize game objects
        self.snake = None
        self.food = None
        self.clock = pygame.time.Clock()
        
    def start(self):
        """Start the game and return the final score"""
        # Initialize game objects
        self.snake = Snake(self.width // 2, self.height // 2, self.cell_size)
        self.food = Food(self.width, self.height, self.cell_size)
        self.score = 0
        self.game_over = False
        self.paused = False
        
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
                    elif not self.paused and not self.game_over:
                        self.snake.handle_key(event.key)
            
            # Update game state if not paused or game over
            if not self.paused and not self.game_over:
                self.update()
            
            # Render game
            self.render()
            
            # Cap the frame rate
            self.clock.tick(10)
        
        return self.score
    
    def update(self):
        """Update game state"""
        # Move snake
        self.snake.move()
        
        # Check for collision with food
        if self.snake.check_collision_with_food(self.food):
            self.score += 10
            self.snake.grow()
            self.food.respawn(self.width, self.height, self.snake.body)
            
            # Play sound
            if "eat" in self.sounds:
                self.sounds["eat"].play()
        
        # Check for collision with walls or self
        if self.snake.check_collision_with_walls(self.width, self.height) or self.snake.check_collision_with_self():
            self.game_over = True
            
            # Play sound
            if "crash" in self.sounds:
                self.sounds["crash"].play()
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw grid
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
        
        # Draw food
        self.food.draw(self.screen)
        
        # Draw snake
        self.snake.draw(self.screen)
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, (0, 255, 0))
        self.screen.blit(score_text, (10, 10))
        
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