import pygame
from Player import Player
import Enemies
from Field import Field
import math
from utils import *

# Initialize Pygame
pygame.init()

# Screen dimensions - increased to fit 800x600 field + UI
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("mQIX")

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 50, 200)
BLACK = (0, 0, 0)
GREEN = (100, 255, 100)

# Fonts
font = pygame.font.SysFont("arialblack", 40)

# Load button image
startbuttonimg = pygame.image.load("images/play-button.jpg").convert_alpha()
startButton = Button(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2, startbuttonimg, 0.25)

game_field = Field(
    x=(SCREEN_WIDTH - 800) // 2,  # Still ~800px wide (160 tiles * 5px)
    y=50,
    width=160,  # 160 tiles
    height=120  # 120 tiles
)
# Create the Player object
player = Player(game_field)

# Create the Sparc (enemy) object
sparc = Enemies.Sparc(game_field)
sparc2 = Enemies.Sparc(game_field)
sparc2.reverse_direction()

qix = Enemies.Qix(game_field, size=12)

# Game state
game_started = False  
game_over = False
capture_percentage = 0  # Initialize capture percentage

def draw_menu():
    screen.fill(WHITE)
    title_text = font.render("mQIX", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    if startButton.draw(screen):  
        return True  # Button clicked
    
    pygame.display.flip()
    return False

def render_game():
    """Render all game elements"""
    # Clear screen
    screen.fill(WHITE)
    
    # Draw the field with captured areas and wires
    game_field.draw(screen)
    
    # Draw player and enemy
    player.draw(screen)
    sparc.draw(screen)
    sparc2.draw(screen)
    qix.draw(screen)
    # Draw UI elements
    player.draw_health_bar(screen, SCREEN_HEIGHT)
    
    # Display capture percentage
    font_small = pygame.font.SysFont(None, 36)
    capture_text = font_small.render(f"Captured: {int(capture_percentage)}%", True, BLACK)
    screen.blit(capture_text, (20, 20))
    
    # Game over message
    if game_over:
        font_large = pygame.font.SysFont(None, 72)
        if player.health <= 0:
            text = font_large.render("GAME OVER", True, (255, 0, 0))
        else:
            text = font_large.render("YOU WIN!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)
        
        restart_text = font_large.render("Press R to restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
        screen.blit(restart_text, restart_rect)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # print(game_field.capture_percentage())
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                # Reset game state
                game_field = Field(
                    x=(SCREEN_WIDTH - 800) // 2,  # Still ~800px wide (160 tiles * 5px)
                    y=50,
                    width=160,  # 160 tiles
                    height=120  # 120 tiles
                )
                player = Player(game_field)
                sparc = Enemies.Sparc(game_field)
                sparc2 = Enemies.Sparc(game_field)
                game_over = False
                capture_percentage = 0
    
    # Get current key states
    keys = pygame.key.get_pressed()
    
    if not game_started:
        game_started = draw_menu()
    else:
        if not game_over:
            # Handle game logic
            player.move(keys)
            sparc.move()
            sparc2.move()
            qix.move()
            
            # Check for player-Sparc collisions
            for enemy in [sparc, sparc2]:
                # Simple distance-based collision detection
                distance = math.sqrt((player.position[0] - enemy.position[0])**2 + 
                                   (player.position[1] - enemy.position[1])**2)
                collision_threshold = player.size + enemy.size  # Sum of their sizes
                
                if distance < collision_threshold:
                    enemy.reverse_direction()
                    player.health -= 10  # Deduct health
                    # print(f"Player hit! Health now: {player.health}")
                    
                    # Optional: Add visual feedback
                    pygame.time.set_timer(pygame.USEREVENT, 200)  # Reset color after 200ms
                    
            
            qix_distance = math.sqrt((player.position[0] - qix.position[0])**2 + 
                                   (player.position[1] - qix.position[1])**2)
            qix_collision_threshold = player.size + qix.size  
            if qix_distance < qix_collision_threshold:
                qix.reset_to_uncaptured_area()
                player.health -= 25
                pygame.time.set_timer(pygame.USEREVENT, 200)

            # Sum of their sizes
            # Handle the color reset event
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    player.color = (0, 255, 0)  # Reset to green
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
            
            # Update game state
            if player.health <= 0:
                game_over = True
            
            # Calculate capture percentage using Field's method
            capture_percentage = game_field.capture_percentage()
            
            # Check win condition
            if capture_percentage >= 80:
                game_over = True
        
        # Render everything
        render_game()
    # Update display
    pygame.display.flip()
    clock.tick(100)
        
pygame.quit()