import pygame
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.captured = False
        self.is_border = False
        self.is_wire = False
        self.color = (200, 200, 200)  # Default uncaptured color

    def capture(self):
        """Mark this tile as captured"""
        self.captured = True
        self.is_wire = False  # Reset wire status when captured
        self.color = (100,255,100)

    def set_wire(self):
        """Mark this tile as part of a wire"""
        self.is_wire = True

    def draw(self, surface, field_x, field_y):
        """
        Draw the tile on the given surface
        
        Args:
            surface (pygame.Surface): Surface to draw on
            field_x (int): x-position of the field's top-left corner
            field_y (int): y-position of the field's top-left corner
        """
        rect = pygame.Rect(
            field_x + self.x,
            field_y + self.y,
            self.size,
            self.size
        )
        
        if self.is_wire:
            pygame.draw.rect(surface, self.wire_color, rect)
        elif self.captured:
            pygame.draw.rect(surface, self.capture_color, rect)
        else:
            pygame.draw.rect(surface, self.uncaptured_color, rect)

class Wire:
    def __init__(self, x, y):
        """
        A wire segment that marks the player's path when capturing territory
        
        Args:
            x (int): x-coordinate in the field grid
            y (int): y-coordinate in the field grid
        """
        self.x = x
        self.y = y
        self.color = (255, 0, 0)  # Gray color for wires
        self.size = 1  # Same size as tiles (1 pixel)
        
    def draw(self, surface, field_x, field_y):
        """
        Draw the wire segment on the playing field
        
        Args:
            surface (pygame.Surface): The game screen surface
            field_x (int): x-position of field's top-left corner
            field_y (int): y-position of field's top-left corner
        """
        rect = pygame.Rect(
            field_x + self.x,
            field_y + self.y,
            self.size,
            self.size
        )
        pygame.draw.rect(surface, self.color, rect)