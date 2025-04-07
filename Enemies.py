import pygame
import math
import random

TILE_SIZE = 5

class Sparc():
    def __init__(self, field, speed=3, size=5):
        self.field = field
        self.speed = speed  # Movement speed (pixels per frame)
        self.size = size    # Visual size
        self.color = (255, 0, 0)  # Base color
        self.last_update_time = pygame.time.get_ticks()
        # Movement directions (right, down, left, up)
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        # Initialize at random border position
        self.tile_x, self.tile_y = self.get_random_border_position()
        self.set_initial_direction()
        self.position = self.calculate_pixel_position()
        
        # Movement state
        self.sub_pos = 0.0  # Sub-tile position (0.0-1.0)
        self.update_next_tile()

    def is_valid_position(self, x, y):
        """Check if position is on any border and within bounds"""
        return (0 <= x < self.field.width and 
                0 <= y < self.field.height and
                (self.field.is_on_border(x, y) or 
                 (x, y) in self.field.created_borders))

    def is_on_border(self, x=None, y=None):
        """EXACTLY matches player's border detection logic"""
        if x is None or y is None:
            x, y = self.tile_x, self.tile_y
        return self.field.is_on_border(x, y) or (x, y) in self.field.created_borders

    def move(self):
        """Your working movement with speed control added"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time < (1000 / (self.speed * 10)):  # Speed-based delay
            return
            
        self.last_update_time = current_time
        
        # Your existing direction finding logic
        valid_dirs = []
        for dir_idx, (dir_dx, dir_dy) in enumerate(self.directions):
            check_x, check_y = self.tile_x + dir_dx, self.tile_y + dir_dy
            if self.is_on_border(check_x, check_y):
                valid_dirs.append(dir_idx)
        
        if valid_dirs:
            if len(valid_dirs) > 1 and (self.current_dir + 2) % 4 in valid_dirs:
                valid_dirs.remove((self.current_dir + 2) % 4)
            
            self.current_dir = random.choice(valid_dirs)
            dx, dy = self.directions[self.current_dir]
            self.tile_x += dx
            self.tile_y += dy
        
        self.update_position()
        self.update_next_tile()

    def reverse_direction(self):
        """Simpler reverse that just flips direction"""
        self.current_dir = (self.current_dir + 2) % 4
        self.sub_pos = 1.0 - self.sub_pos


    # def reverse_direction(self):
    #     """Reverse direction with position correction"""
    #     self.current_dir = (self.current_dir + 2) % 4
    #     self.sub_pos = 1.0 - self.sub_pos
    #     self.update_next_tile()
        
    #     # Move immediately to prevent sticking
    #     dx, dy = self.directions[self.current_dir]
    #     new_x = self.tile_x + dx
    #     new_y = self.tile_y + dy
    #     if self.is_valid_position(new_x, new_y):
    #         self.tile_x, self.tile_y = new_x, new_y
    #         self.update_next_tile()

    def update_next_tile(self):
        """Calculate next tile in current direction"""
        dx, dy = self.directions[self.current_dir]
        self.next_tile_x = self.tile_x + dx
        self.next_tile_y = self.tile_y + dy

    def get_random_border_position(self):
        """Return random (x,y) tile coordinates on original border"""
        border_positions = []
        
        # Top and bottom borders
        for x in range(self.field.width):
            border_positions.append((x, 0))  # Top
            border_positions.append((x, self.field.height-1))  # Bottom
            
        # Left and right borders (excluding corners)
        for y in range(1, self.field.height-1):
            border_positions.append((0, y))  # Left
            border_positions.append((self.field.width-1, y))  # Right
            
        return random.choice(border_positions)

    def set_initial_direction(self):
        """Set initial movement direction based on spawn position"""
        if self.tile_y == 0:  # Top border
            self.current_dir = 0  # Right
        elif self.tile_y == self.field.height-1:  # Bottom border
            self.current_dir = 2  # Left
        elif self.tile_x == 0:  # Left border
            self.current_dir = 1  # Down
        else:  # Right border
            self.current_dir = 3  # Up

    def calculate_pixel_position(self):
        """Convert tile coordinates to pixel position (center point)"""
        return (
            self.field.x + self.tile_x * TILE_SIZE + TILE_SIZE//2,
            self.field.y + self.tile_y * TILE_SIZE + TILE_SIZE//2
        )

    def update_position(self):
        """Update pixel position with sub-tile precision"""
        dx, dy = self.directions[self.current_dir]
        self.position = (
            self.field.x + (self.tile_x + self.sub_pos * dx) * TILE_SIZE + TILE_SIZE//2,
            self.field.y + (self.tile_y + self.sub_pos * dy) * TILE_SIZE + TILE_SIZE//2
        )

    def draw(self, surface):
        """Draw diamond shape with border type indication"""
        # Color based on border type
        border_color = (255, 100, 100) if (self.tile_x, self.tile_y) in self.field.created_borders else self.color
        
        points = [
            (self.position[0] + self.size, self.position[1]),
            (self.position[0], self.position[1] + self.size),
            (self.position[0] - self.size, self.position[1]),
            (self.position[0], self.position[1] - self.size)
        ]
        pygame.draw.polygon(surface, border_color, points)


class Qix():
    def __init__(self, field, speed=3.0, size=12):
        self.field = field
        self.speed = speed  # Constant speed (faster than original)
        self.size = size
        self.color = (255, 165, 0)  # Orange
        self.last_update_time = pygame.time.get_ticks()
        
        # Movement variables
        self.direction = random.uniform(0, 2 * math.pi)  # Random initial angle
        self.x_vel = math.cos(self.direction) * self.speed
        self.y_vel = math.sin(self.direction) * self.speed
        
        # Initialize position
        self.reset_to_uncaptured_area()
        self.position = self.calculate_pixel_position()

    def reset_to_uncaptured_area(self):
        """Teleport Qix to a random position in uncaptured area"""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(1, self.field.width-2)
            y = random.randint(1, self.field.height-2)
            if not self.field.is_captured(x, y) and not self.field.is_on_border(x, y):
                self.tile_x = x
                self.tile_y = y
                return
        
        # Fallback if no uncaptured area found (shouldn't happen in normal game)
        self.tile_x = random.randint(1, self.field.width-2)
        self.tile_y = random.randint(1, self.field.height-2)

    def calculate_pixel_position(self):
        """Convert tile coordinates to pixel position (center point)"""
        return (
            self.field.x + self.tile_x * TILE_SIZE + TILE_SIZE//2,
            self.field.y + self.tile_y * TILE_SIZE + TILE_SIZE//2
        )
    
    def is_position_valid(self, x, y):
        """Check if position is uncaptured and not a border"""
        return (0 <= x < self.field.width and 
                0 <= y < self.field.height and
                not self.field.is_on_border(x, y) and 
                not self.field.is_captured(x, y))

    def move(self):
        """Smooth movement with random direction changes"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time < (1000 / (self.speed * 20)):
            return
        self.last_update_time = current_time

        # Check if current position became invalid (captured)
        if not self.is_position_valid(int(self.tile_x), int(self.tile_y)):
            self.reset_to_uncaptured_area()
            self.direction = random.uniform(0, 2 * math.pi)  # New random direction
            self.x_vel = math.cos(self.direction) * self.speed
            self.y_vel = math.sin(self.direction) * self.speed
            return

        # Calculate new position
        new_x = self.tile_x + self.x_vel / TILE_SIZE
        new_y = self.tile_y + self.y_vel / TILE_SIZE

        # If hitting a barrier, change direction
        if not self.is_position_valid(int(new_x), int(new_y)):
            self.direction = random.uniform(0, 2 * math.pi)
            self.x_vel = math.cos(self.direction) * self.speed
            self.y_vel = math.sin(self.direction) * self.speed
        else:
            # Apply movement
            self.tile_x = new_x
            self.tile_y = new_y

        # Small chance for random direction change
        if random.random() < 0.05:  # 5% chance per move
            self.direction += random.uniform(-1, 1)  # More noticeable changes
            self.direction %= 2 * math.pi
            self.x_vel = math.cos(self.direction) * self.speed
            self.y_vel = math.sin(self.direction) * self.speed

        self.update_position()

    def update_position(self):
        """Convert tile position to pixel position"""
        self.position = (
            self.field.x + self.tile_x * TILE_SIZE + TILE_SIZE//2,
            self.field.y + self.tile_y * TILE_SIZE + TILE_SIZE//2
        )

    def draw(self, surface):
        """Draw Qix with pulsating effect"""
        # Pulsing animation
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        current_size = self.size * (0.8 + pulse * 0.4)
        
        # Main body
        pygame.draw.circle(surface, self.color, 
                         (int(self.position[0]), int(self.position[1])), 
                         int(current_size))
        
        # Inner pattern
        inner_size = current_size * 0.6
        pygame.draw.circle(surface, (255, 255, 255), 
                         (int(self.position[0]), int(self.position[1])), 
                         int(inner_size), 2)