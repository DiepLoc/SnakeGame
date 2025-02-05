# Import and initialize the pygame library
import pygame
import random

pygame.init()

width = 500
height = 500
dt = 0 # delta time - seconds

screen = pygame.display.set_mode([width, height])
clock = pygame.time.Clock()

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


    ## Draw
    # Fill the background with white
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (100,100,100), (50, 50), 10)

    # Flip the display
    pygame.display.flip()

    dt = clock.tick(60) / 1000
# Done! Time to quit.
pygame.quit()