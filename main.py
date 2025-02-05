# Import and initialize the pygame library
import pygame
import random
import constants
from snake import *

pygame.init()

dt = 0  # delta time - seconds

screen = pygame.display.set_mode([constants.windowWidth, constants.windowHeight])
clock = pygame.time.Clock()

snake = Snake()


# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mouses = pygame.mouse.get_pressed()

    ## Update
    snake.update(dt)

    ## Draw
    # Fill the background with white
    screen.fill((0, 0, 0))
    snake.draw(screen, dt)
    # Flip the display
    pygame.display.flip()

    dt = clock.tick(60) / 1000
# Done! Time to quit.
pygame.quit()
