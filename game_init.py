
import pygame

from camera import CameraGroup
from floor import initiate_floor
from gamestate import Gamestate
from hero import Hero
from map_objects import create_animated_fires, create_trees

import sys
import os

from utilities import charger_save, sauvegarder_save

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from pathlib import Path
import json

save_file = Path("save.json")

# Création du fichier s'il n'existe pas
if not save_file.exists():
    save = {
        "noms": [],
        "gold": 0
    }
    sauvegarder_save(save)
else: 
    save = charger_save()



# Signal de départ pour la logique du jeu, activé après la fin des menus ou des tutoriels
game_has_started = False

pygame.init()
gamestate = Gamestate(save)

initiate_floor(gamestate)
camera_group = CameraGroup(gamestate)


# Création du héros
hero = Hero(gamestate)
hero.velocity = 0  # le héros ne doit pas pouvoir bouger pendant le tuto


# Initialisation de l'outil de génération des vagues d'ennemis

# Choix du titre de la fenêtre, c'est une ref à une série coréenne...
pygame.display.set_caption("Un blob scaccia l'altro")

# Initialisation de l'heure du début du jeu (pour la logique)
time_of_real_start = 0

# Initialisation de l'horloge
clock = pygame.time.Clock()

# Initialisation de la musique
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

# Création des objets de la map, cela devrait sûrement être ailleurs
# create_fire((start_draw_x + i * dim_tile[0], start_draw_y + j*dim_tile[1]), 0.5)
create_trees(gamestate, 100)
create_animated_fires(gamestate, 100)

# gamestate.is_paused = True  # le jeu est en pause pendant les menus de départ

# Gestion des menus de départ
starting_menu = 1


music_paused = False
last_music_flip = -9999999999

