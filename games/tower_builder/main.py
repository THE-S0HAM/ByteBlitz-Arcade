import pygame
import sys
import random
import os

# Game information dictionary
GAME_INFO = {
    "title": "Tower Builder",
    "description": "Stack blocks to build the tallest tower",
    "author": "ByteBlitz Team",
    "version": "1.0"
}

class Block:
    """Stackable block"""
    
    def __init__(self, x, y, width, height, speed, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.direction = 1  # 1 for right, -1 for left
    
    def move(self, screen_width):
        """Move the block horizontally"""
        self.x += self.speed * self.direction
        
        # Change direction if hitting screen edge
        if self.x <= 0 or self.x + self.width >= screen_width:
            self.direction *= -1
    
    def draw(self, screen):
        """Draw the block on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Add a highlight effect
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, 5))
    
    def drop(self, target_y):
        """Drop the block to the target y position"""
        self.y = target_y
    
    def slice(self, x_offset):
        """Slice the block based on overlap with previous block"""
        # Reduce width by the offset amount
        new_width = self.width - abs(x_offset)
        
        # Adjust x position if needed
        if x_offset > 0:
            self.x += x_offset
            
        # Update width
        self.width = max(10, new_width)  # Minimum width of 10
        
        # Return the new width
        return self.width


class Game:
    """Tower Builder game implementation"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.bg_color = (50, 50, 80)  # Dark blue-gray
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Block properties
        self.block_height = 20
        self.initial_block_width = 200
        self.block_speed = 2
        
        # Tower properties
        self.tower_base_y = self.height - 100
        self.tower_blocks = []
        
        # Current moving block
        self.current_block = None
        
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
        self.sound_dir = os.path.join("games", "tower_builder", "assets", "sounds")
        self.sounds = {}
        
        # Initialize game objects
        self.clock = pygame.time.Clock()
        
        # Create the first block
        self.create_first_block()
    
    def create_first_block(self):
        """Create the first block at the base of the tower"""
        x = (self.width - self.initial_block_width) // 2
        y = self.tower_base_y
        color = self.get_random_color()
        
        # Create a stationary base block
        base_block = Block(x, y, self.initial_block_width, self.block_height, 0, color)
        self.tower_blocks.append(base_block)
        
        # Create the first moving block
        self.create_new_block()
    
    def create_new_block(self):
        """Create a new moving block"""
        # Increase speed slightly with each block
        speed = min(self.block_speed + self.score * 0.1, 8)
        
        # Start position
        x = 0
        y = self.tower_base_y - (len(self.tower_blocks) * self.block_height)
        
        # Get width from previous block
        width = self.tower_blocks[-1].width
        
        # Random color
        color = self.get_random_color()
        
        # Create the block
        self.current_block = Block(x, y, width, self.block_height, speed, color)
    
    def get_random_color(self):
        """Generate a random bright color"""
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        return (r, g, b)
    
    def place_block(self):
        """Place the current block on the tower"""
        if not self.current_block:
            return False
            
        # Get the previous block
        prev_block = self.tower_blocks[-1]
        
        # Calculate overlap
        x_offset = self.current_block.x - prev_block.x
        
        # Check if block is completely off
        if (x_offset >= prev_block.width or 
            x_offset <= -self.current_block.width):
            self.game_over = True
            return False
        
        # Slice the block based on overlap
        new_width = self.current_block.slice(x_offset)
        
        # Add to tower
        self.tower_blocks.append(self.current_block)
        
        # Increase score
        self.score += 1
        
        # Create a new block
        self.create_new_block()
        
        return True
    
    def start(self):
        """Start the game and return the final score"""
        # Reset game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.tower_blocks = []
        
        # Create the first block
        self.create_first_block()
        
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
                        self.place_block()
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
        # Move current block
        if self.current_block:
            self.current_block.move(self.width)
            
        # Scroll view if tower gets too tall
        if len(self.tower_blocks) > 15:
            # Calculate how much to scroll
            scroll_amount = self.block_height
            
            # Move all blocks down
            for block in self.tower_blocks:
                block.y += scroll_amount
            
            # Remove blocks that are off screen
            while (self.tower_blocks and 
                   self.tower_blocks[0].y > self.height):
                self.tower_blocks.pop(0)
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw tower blocks
        for block in self.tower_blocks:
            block.draw(self.screen)
        
        # Draw current block
        if self.current_block and not self.game_over:
            self.current_block.draw(self.screen)
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw instructions
        if not self.game_over and self.score == 0:
            instr_text = self.font_small.render("Press SPACE to place blocks", True, (255, 255, 255))
            self.screen.blit(instr_text, 
                            (self.width // 2 - instr_text.get_width() // 2, 
                             50))
        
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