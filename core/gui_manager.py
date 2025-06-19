import pygame
import os
import math
import random

class GUIManager:
    """Manages GUI components and styling for the arcade hub"""
    
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.fonts = {}
        self.colors = {
            'neon_blue': (0, 195, 255),
            'neon_pink': (255, 16, 240),
            'neon_green': (57, 255, 20),
            'neon_yellow': (255, 254, 0),
            'neon_orange': (255, 128, 0),
            'neon_purple': (180, 0, 255),
            'dark_bg': (0, 0, 15),
            'light_text': (255, 255, 255),
            'grid_line': (20, 20, 40)
        }
        self.load_fonts()
        self.particles = []
        self.time = 0
        
    def load_fonts(self):
        """Load fonts for the GUI"""
        # Use clear, bold fonts that look arcade-like
        self.fonts['title'] = pygame.font.SysFont("arial", 48, bold=True)
        self.fonts['heading'] = pygame.font.SysFont("arial", 32, bold=True)
        self.fonts['normal'] = pygame.font.SysFont("arial", 24, bold=True)
        self.fonts['small'] = pygame.font.SysFont("arial", 18, bold=True)
    
    def update(self):
        """Update animations and effects"""
        self.time += 1
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
    
    def draw_background(self):
        """Draw retro grid background"""
        width, height = self.screen.get_size()
        
        # Draw dark background
        self.screen.fill(self.colors['dark_bg'])
        
        # Draw grid lines
        grid_spacing = 40
        grid_color = self.colors['grid_line']
        
        # Draw horizontal grid lines
        for y in range(0, height, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (width, y), 1)
        
        # Draw vertical grid lines
        for x in range(0, width, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, height), 1)
        
        # Draw some random stars
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), size)
    
    def draw_text(self, text, font_name, color, x, y, align="center", glow=False, shadow=True):
        """Draw text on the screen with specified alignment and effects"""
        font = self.fonts.get(font_name, self.fonts['normal'])
        color_value = self.colors.get(color, color)
        
        # Always draw shadow for better visibility
        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect()
            
            if align == "center":
                shadow_rect.center = (x + 2, y + 2)
            elif align == "left":
                shadow_rect.topleft = (x + 2, y + 2)
            elif align == "right":
                shadow_rect.topright = (x + 2, y + 2)
                
            self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw glow effect for better visibility
        if glow:
            glow_size = 2
            glow_color = list(color_value)
            for i in range(3):
                glow_color[i] = min(255, glow_color[i] + 50)
            
            for offset_x, offset_y in [(-glow_size, 0), (glow_size, 0), (0, -glow_size), (0, glow_size)]:
                glow_surface = font.render(text, True, glow_color)
                glow_rect = glow_surface.get_rect()
                
                if align == "center":
                    glow_rect.center = (x + offset_x, y + offset_y)
                elif align == "left":
                    glow_rect.topleft = (x + offset_x, y + offset_y)
                elif align == "right":
                    glow_rect.topright = (x + offset_x, y + offset_y)
                    
                self.screen.blit(glow_surface, glow_rect)
        
        # Draw main text
        text_surface = font.render(text, True, color_value)
        text_rect = text_surface.get_rect()
        
        if align == "center":
            text_rect.center = (x, y)
        elif align == "left":
            text_rect.topleft = (x, y)
        elif align == "right":
            text_rect.topright = (x, y)
            
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_button(self, text, font_name, x, y, width, height, idle_color, hover_color=None, align="center"):
        """Draw an arcade-style button and return if it's clicked"""
        hover_color = hover_color or idle_color
        
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        # Create button rect
        button_rect = pygame.Rect(0, 0, width, height)
        if align == "center":
            button_rect.center = (x, y)
        elif align == "left":
            button_rect.topleft = (x, y)
        elif align == "right":
            button_rect.topright = (x, y)
        
        # Check hover state
        hovered = button_rect.collidepoint(mouse_pos)
        if hovered:
            color = hover_color
            if pygame.mouse.get_pressed()[0]:
                clicked = True
                # Add particles on click
                self.add_particles(button_rect.centerx, button_rect.centery, 10, idle_color)
        else:
            color = idle_color
        
        # Draw button with 3D effect
        pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
        
        # Draw button border with neon glow effect
        border_color = list(color)
        for i in range(3):
            border_color[i] = min(255, border_color[i] + 50)
        
        # Inner border
        pygame.draw.rect(self.screen, border_color, button_rect, 3, border_radius=5)
        
        # Outer glow if hovered
        if hovered:
            pygame.draw.rect(self.screen, border_color, 
                            button_rect.inflate(6, 6), 2, border_radius=7)
            pygame.draw.rect(self.screen, border_color, 
                            button_rect.inflate(12, 12), 1, border_radius=9)
        
        # Draw text with shadow
        font = self.fonts.get(font_name, self.fonts['normal'])
        
        # Shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(button_rect.center[0] + 2, button_rect.center[1] + 2))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Main text
        text_surface = font.render(text, True, self.colors['light_text'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return clicked, button_rect
    
    def draw_panel(self, x, y, width, height, color=None, alpha=230, border=True):
        """Draw an arcade-style panel with neon border"""
        if color is None:
            color = self.colors['dark_bg']
            
        # Create panel surface with alpha
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((*color[:3], alpha))
        
        # Draw panel
        self.screen.blit(panel, (x, y))
        
        # Draw border with neon effect
        if border:
            border_color = self.colors['neon_blue']
            pulse = (math.sin(self.time / 20) + 1) * 0.5  # Pulsing effect
            
            # Adjust brightness based on pulse
            glow_color = list(border_color)
            for i in range(3):
                glow_color[i] = min(255, int(border_color[i] + 50 * pulse))
            
            # Draw multiple borders for glow effect
            pygame.draw.rect(self.screen, glow_color, 
                            (x, y, width, height), 3, border_radius=3)
            pygame.draw.rect(self.screen, (*glow_color, 150), 
                            (x-2, y-2, width+4, height+4), 2, border_radius=4)
            pygame.draw.rect(self.screen, (*glow_color, 100), 
                            (x-4, y-4, width+8, height+8), 1, border_radius=5)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_title(self, text, x, y):
        """Draw an arcade-style title with effects"""
        # Draw multiple layers for glow effect
        colors = [
            self.colors['neon_pink'],
            self.colors['neon_blue'],
            self.colors['light_text']
        ]
        
        offsets = [(4, 4), (2, 2), (0, 0)]
        
        for color, offset in zip(colors, offsets):
            self.draw_text(text, 'title', color, x + offset[0], y + offset[1], 
                          align="center", shadow=True)
        
        # Add some decorative elements
        width = self.fonts['title'].size(text)[0]
        line_y = y + 30
        line_length = width * 0.8
        
        # Draw decorative lines
        pygame.draw.line(self.screen, self.colors['neon_blue'], 
                        (x - line_length/2, line_y), (x + line_length/2, line_y), 3)
        
        # Draw small decorative elements at the ends
        pygame.draw.circle(self.screen, self.colors['neon_pink'], 
                          (int(x - line_length/2), line_y), 5)
        pygame.draw.circle(self.screen, self.colors['neon_pink'], 
                          (int(x + line_length/2), line_y), 5)
    
    def add_particles(self, x, y, count, color):
        """Add particles for visual effects"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            size = random.randint(2, 4)
            life = random.randint(20, 40)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': life
            })
    
    def draw_particles(self):
        """Draw all active particles"""
        for particle in self.particles:
            alpha = min(255, int(255 * (particle['life'] / 40)))
            color = list(particle['color'])
            pygame.draw.circle(self.screen, (*color[:3], alpha), 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])