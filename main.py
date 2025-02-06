# Import and initialize the pygame library
import pygame
import random
import constants
from snake import *
from player import *

pygame.init()

dt = 0  # delta time - seconds

screen = pygame.display.set_mode([constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT])
clock = pygame.time.Clock()

snake = Snake()
player = Player()

# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        player.handleEvent(event)

    pressed_keys = pygame.key.get_pressed()
    pressed_mouses = pygame.mouse.get_pressed()

    ## Update
    player.update(dt, events)
    snake.update(dt, player)

    ## Draw
    # Fill the background with white
    screen.fill((0, 0, 0))

    snake.draw(screen, dt)
    player.draw(screen)
    # Flip the display
    pygame.display.flip()

    dt = clock.tick(60) / 1000 * constants.GAME_SPEED_SCALE
# Done! Time to quit.
pygame.quit()
