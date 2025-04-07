import pygame
import math
from utils import *

TILE_SIZE = 5  # Reduced from 10px to 5px for finer movement
BORDER_WIDTH = 1  # Border remains 1 tile wide

class Field:
    def __init__(self, x, y, width=160, height=120, color=(200, 200, 200), border_width=BORDER_WIDTH):
        # Double tile count to maintain similar play area size (160x120 tiles = 800x600 pixels)
        self.x = x
        self.y = y
        self.width = width  
        self.height = height
        self.color = color
        self.border_width = border_width
        self.created_borders = set()
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        self.rect = pygame.Rect(x, y, self.pixel_width, self.pixel_height)
        
        # Initialize tiles matrix
        self.tiles = []
        for y_pos in range(height):
            row = []
            for x_pos in range(width):
                row.append(Tile(x_pos, y_pos))
            self.tiles.append(row)
        
        # Initialize perimeter and captured status
        self.perimeter = set()
        self.wires = []
        self.wire_coordinates = []
        
        # Create border tiles
        self.create_border_tiles()
        self.capture_edges()
        self.update_perimeter()

    def create_border_tiles(self):
        """Create 1-tile wide borders around the edges"""
        # Top border
        y = 0
        for x in range(self.width):
            self.tiles[y][x].is_border = True
            self.tiles[y][x].color = (0, 0, 0)
        
        # Bottom border
        y = self.height - 1
        for x in range(self.width):
            self.tiles[y][x].is_border = True
            self.tiles[y][x].color = (0, 0, 0)
        
        # Left border
        x = 0
        for y in range(1, self.height - 1):
            self.tiles[y][x].is_border = True
            self.tiles[y][x].color = (0, 0, 0)
        
        # Right border
        x = self.width - 1
        for y in range(1, self.height - 1):
            self.tiles[y][x].is_border = True
            self.tiles[y][x].color = (0, 0, 0)

    def capture_edges(self):
        """Capture the edges of the field (border tiles)"""
        border_count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].is_border:
                    self.tiles[y][x].capture()
                    border_count += 1
        # # Calculate expected border percentage
        # total_border = 2 * (self.width + self.height - 2)  # Formula for perimeter tiles
        # # print(f"Captured {border_count} border tiles (should be {total_border})")
    
    def is_on_border(self, x, y):
        """Check if position is on any border (original or created)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].is_border
        return False

    def are_adjacent(self, pos1, pos2):
        """Check if two positions are adjacent (including diagonally)"""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

    def is_captured(self, x, y):
        """Check if a position is captured"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].captured
        return True  # Consider outside as captured

    def update_perimeter(self):
        """Include created borders in perimeter"""
        self.perimeter = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.is_captured(x, y) or (x, y) in self.created_borders:
                    # Check adjacent tiles
                    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < self.width and 0 <= ny < self.height and 
                            not self.is_captured(nx, ny) and 
                            (nx, ny) not in self.created_borders):
                            self.perimeter.add((x, y))
                            break

    def draw(self, surface):
        """Optimized drawing - only draw visible tiles"""
        # Calculate visible area
        view_x = max(0, (0 - self.x) // TILE_SIZE)
        view_y = max(0, (0 - self.y) // TILE_SIZE)
        view_width = min(self.width, (surface.get_width() - self.x) // TILE_SIZE + 1)
        view_height = min(self.height, (surface.get_height() - self.y) // TILE_SIZE + 1)
        
        for y in range(view_y, view_height):
            for x in range(view_x, view_width):
                tile = self.tiles[y][x]
                rect = pygame.Rect(
                    self.x + x * TILE_SIZE,
                    self.y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                if tile.is_wire:
                    pygame.draw.rect(surface, (150, 150, 150), rect)
                elif tile.is_border:
                    pygame.draw.rect(surface, (0, 0, 0), rect)
                elif tile.captured:
                    pygame.draw.rect(surface, (100, 255, 100), rect)
                else:
                    pygame.draw.rect(surface, (200, 200, 200), rect)

    def push(self, x, y):
        """Prevent adding wires to border tiles"""
        if (0 <= x < self.width and 0 <= y < self.height and 
            not self.tiles[y][x].is_border):  # Add this check
            if (x, y) not in self.wire_coordinates:
                self.wires.append(Wire(x, y))
                self.wire_coordinates.append((x, y))
                self.tiles[y][x].is_wire = True
    
    def capture_area(self):
        """Capture the area enclosed by wires"""
        if len(self.wires) < 2:  # Need at least 2 points to determine direction
            self.wires = []  # Reset wires if invalid
            self.wire_coordinates = []
            return
        
        capture_trail = set(self.wire_coordinates)
        # Capture all wire positions
        for wire in self.wires:
            if 0 <= wire.x < self.width and 0 <= wire.y < self.height:
                self.tiles[wire.y][wire.x].capture()
                self.tiles[wire.y][wire.x].is_wire = False
        
        # Determine flood fill starting points
        direction = (self.wires[0].x - self.wires[1].x, self.wires[0].y - self.wires[1].y)
        
        # Create temporary matrices for flood fill
        temp_left = [[False for _ in range(self.width)] for _ in range(self.height)]
        temp_right = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                temp_left[y][x] = self.is_captured(x, y)
                temp_right[y][x] = self.is_captured(x, y)
        
        # Flood fill both sides
        if direction[0]:  # Horizontal movement
            self.flood_fill(temp_left, self.wires[1].x, self.wires[1].y + 1)
            self.flood_fill(temp_right, self.wires[1].x, self.wires[1].y - 1)
        else:  # Vertical movement
            self.flood_fill(temp_left, self.wires[1].x + 1, self.wires[1].y)
            self.flood_fill(temp_right, self.wires[1].x - 1, self.wires[1].y)
        
        # Choose the smaller area to capture
        left_count = sum(sum(row) for row in temp_left)
        right_count = sum(sum(row) for row in temp_right)
        
        target = temp_left if left_count < right_count else temp_right
        
        # Apply the capture
        for y in range(self.height):
            for x in range(self.width):
                if target[y][x]:
                    self.tiles[y][x].capture()
        
        for x, y in capture_trail:
            if not self.tiles[y][x].is_border and self.tiles[y][x].captured:  # Don't convert original borders
                self.tiles[y][x].is_border = True
                self.tiles[y][x].color = (0, 0, 0)  # Black
                
                self.created_borders.add((x, y))
        # Reset wires and update perimeter
        self.wires = []
        self.wire_coordinates = []
        self.update_perimeter()


    def flood_fill(self, matrix, x, y):
        """Stack-based flood fill to avoid recursion limits"""
        stack = [(x, y)]
        while stack:
            x, y = stack.pop()
            if (0 <= x < self.width and 0 <= y < self.height and 
                not matrix[y][x]):
                matrix[y][x] = True
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))

    def capture_percentage(self):
        """Calculate percentage of captured area (excluding border tiles)"""
        total_capturable = 0
        captured = 0
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.tiles[y][x].is_border:  # Skip border tiles
                    total_capturable += 1
                    if self.is_captured(x, y):
                        captured += 1
        
        if total_capturable == 0:
            return 0  # Prevent division by zero
        
        return math.floor((captured / total_capturable) * 100)

    def get_tile_rect(self, x, y):
        """Get pygame.Rect for a specific tile"""
        return pygame.Rect(
            self.x + x * TILE_SIZE,
            self.y + y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )