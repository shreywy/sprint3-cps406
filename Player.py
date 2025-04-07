import pygame
import math
from utils import *

TILE_SIZE = 5  # Each tile is 5x5 pixels

class Player():
    def __init__(self, field, color=(0, 255, 0), size=TILE_SIZE):
        self.field = field
        self.health = 100
        self.max_health = 100
        self.color = color
        self.size = size * 2
        self.speed = TILE_SIZE // 2  # Slower movement (originally was TILE_SIZE)
        # Start position perfectly aligned on bottom border
        self.position = (
            field.x + (field.width * TILE_SIZE) // 2 - (size // 2),
            field.y + field.height * TILE_SIZE - field.border_width * TILE_SIZE
        )
        self.on_edge = "bottom"
        self.in_field = False
        self.direction = None
        self.trail = []
        self.capturing = False
        self.capture_start_pos = None

    @property
    def field_x(self):
        """Current x position in tile coordinates"""
        return int((self.position[0] - self.field.x) // TILE_SIZE)

    @property
    def field_y(self):
        """Current y position in tile coordinates"""
        return int((self.position[1] - self.field.y) // TILE_SIZE)

    def draw(self, surface):
        # Draw trail
        if len(self.trail) > 1:
            screen_trail = [(p[0] * TILE_SIZE + self.field.x, 
                            p[1] * TILE_SIZE + self.field.y) for p in self.trail]
            pygame.draw.lines(surface, (200, 200, 200), False, screen_trail, 2)
        
        # Draw player
        color = (0, 200, 0) if self.in_field else self.color
        pygame.draw.rect(surface, color, (*self.position, self.size, self.size))

    def draw_health_bar(self, surface, screen_height=400):
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = screen_height - 40

        # Black outline
        pygame.draw.rect(surface, (0, 0, 0), (bar_x-2, bar_y-2, bar_width+4, bar_height+4))
        # Background
        pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health
        fill_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))
    
    def is_on_border(self, x=None, y=None):
        """Check if player is on or adjacent to border tiles"""
        if x is None or y is None:
            x, y = self.field_x, self.field_y
        return self.field.is_on_border(x, y)

    def move(self, keys):
        """Move the Player at slower speed while maintaining all original logic"""
        new_x, new_y = self.position
        moved = False   
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= self.speed
            moved = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += self.speed
            moved = True
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= self.speed
            moved = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += self.speed
            moved = True

        if moved:
            # Convert to field coordinates
            new_field_pos = (int((new_x - self.field.x) // TILE_SIZE), 
                            int((new_y - self.field.y) // TILE_SIZE))
            current_field_pos = (self.field_x, self.field_y)
            
            shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            # If shift is held (attempting to push into field)
            if shift_pressed:
                if (self.is_on_border() or  
                    (self.capturing and 
                     self.field.are_adjacent(current_field_pos, new_field_pos) and
                     not self.field.is_captured(*new_field_pos))):
                    
                    if not self.capturing:
                        self.capturing = True
                        self.capture_start_pos = current_field_pos
                        self.field.push(*current_field_pos)
                        self.trail.append(current_field_pos)
                    
                    self.position = (new_x, new_y)
                    self.field.push(*new_field_pos)
                    self.trail.append(new_field_pos)
                
                elif (self.capturing and 
                      self.is_on_border(*new_field_pos)):
                    
                    self.field.capture_area()
                    self.position = (new_x, new_y)
                    self.trail = []
                    self.capturing = False
                    self.capture_start_pos = None
            
            # Normal movement (along borders)
            else:
                if self.is_on_border(*new_field_pos):
                    self.position = (new_x, new_y)
                    if self.trail:
                        self.trail = []
                        self.capturing = False
                        self.capture_start_pos = None
                else:
                    self.snap_to_border()

            if self.field.is_on_border(*new_field_pos):
                self.position = (new_x, new_y)
                if self.trail:
                    self.trail = []
                    self.capturing = False
                    self.capture_start_pos = None

        self.update_edge_status()
    
    def snap_to_border(self):
        """Adjust position to stay perfectly on border tiles"""
        field_x = self.field_x
        field_y = self.field_y
        
        if field_y < 0:
            self.position = (self.position[0], self.field.y)
        elif field_y >= self.field.height:
            self.position = (self.position[0], 
                           self.field.y + (self.field.height - 1) * TILE_SIZE)
        elif field_x < 0:
            self.position = (self.field.x, self.position[1])
        elif field_x >= self.field.width:
            self.position = (self.field.x + (self.field.width - 1) * TILE_SIZE,
                           self.position[1])
    
    def update_edge_status(self):
        """Update which edge the player is currently on"""
        field_x = self.field_x
        field_y = self.field_y
        
        if field_y == 0:
            self.on_edge = "top"
        elif field_y == self.field.height - 1:
            self.on_edge = "bottom"
        elif field_x == 0:
            self.on_edge = "left"
        elif field_x == self.field.width - 1:
            self.on_edge = "right"
        else:
            self.on_edge = None