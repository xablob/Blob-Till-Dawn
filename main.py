import numpy as np
import pygame
from game import Game

run = True

game = Game()

# Boucle classique de Pygame
while run:
    run = game.update_frame()

pygame.quit()
