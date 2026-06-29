import pygame
from game_init import (
    camera_group,
    clock,
    game_has_started,
    gamestate,
    hero,
    last_music_flip,
    music_paused,
    starting_menu,
)
from mobwave import MobWave
from params import allow_spawn, last_spawn, menu_switch_cooldown, mobs_per_wave, spawn_cd, dimx, dimy

from items import items
from map_objects import map_objects

from projectile import Skillshots, entity_targeted_projectiles
import numpy as np

def update_game(keys_pressed, mouse_pos, mouse_keys, time):
    """Cette fonction met à jour tout le jeu, principalement en appelant les fonctions update de chaque Sprite"""
    # TODO A terme, il faudrait tout mettre dans l'update du gamestate
    gamestate.update(time, keys_pressed, mouse_pos, mouse_keys, Skillshots)
    entity_targeted_projectiles.update()  # il n'y en a pas pour l'instant
    Skillshots.update(
        time
    )  # les projectiles, sauf les boules de feu qui tournent autour du héros, qui elles sont mises à jour dans la méthode update du héros
    map_objects.update()  # les arbres et les feux de la map
    items.update(
        hero, time
    )  # les items despawn au bout d'un certain temps, et chacun checke s'il est en collision avec le héros
    camera_group.update(mouse_pos, time)  # mise à jour de la caméra

class Game:
    def __init__(self):
        self.game_was_paused_last_frame = True
        self.game_is_paused_this_frame = True
        self.total_pause_time = 0
        self.last_pause_start = 0
        self.last_pause_end = 0
        self.last_pause_flip = -999999
        self.real_game_time = 0
        self.last_spawn = -999999999
        self.spawn_cd = spawn_cd
        self.game_has_started = game_has_started
        self.starting_menu = starting_menu
        self.mobs_per_wave = mobs_per_wave
        self.music_paused = music_paused



    def update_mob_spawn(self):
        if (
            self.real_game_time - self.last_spawn > self.spawn_cd
            and hero.alive()
            and allow_spawn
            and self.game_has_started
            and gamestate.is_paused == False
            and gamestate.hero_is_not_paused == True
        ):
            MobWave(self.mobs_per_wave, self.real_game_time)
            self.last_spawn = self.real_game_time
            self.mobs_per_wave += 1.5
            self.spawn_cd -= 200
            self.spawn_cd = max(5000, self.spawn_cd)

    def draw_menus(self, now, event_list, keys):
        if not self.game_has_started:
            match self.starting_menu:
                case 3:
                    gamestate.camera_group.draw_home_screen_3()
                    if keys[pygame.K_RETURN] and now - self.last_menu_switch > menu_switch_cooldown:
                        self.last_menu_switch = now
                        hero.velocity = hero.original_velocity
                        gamestate.is_paused = False
                        self.game_has_started = True
                case 2:
                    gamestate.camera_group.draw_home_screen_2()
                    if keys[pygame.K_RETURN] and now - self.last_menu_switch > menu_switch_cooldown:
                        self.starting_menu += 1
                        self.last_menu_switch = now
                case 1:
                    gamestate.camera_group.draw_home_screen_1(event_list)
                    if gamestate.name_has_been_entered:
                        self.starting_menu += 1
                        self.last_menu_switch = now
    
    def update_music(self, keys):
        if keys[pygame.K_m] and self.real_game_time - self.last_music_flip > 100:
            if self.music_paused:
                pygame.mixer.music.unpause()
                self.music_paused = False
            else:
                pygame.mixer.music.pause()
                self.music_paused = True
            self.last_music_flip = self.real_game_time

    def update_pause(self, now, keys):
        # On stocke l'état de la frame d'avant
        self.game_was_paused_last_frame = self.game_is_paused_this_frame

        # Update avec les actions du joueur
        if keys[pygame.K_p] and self.real_game_time - self.last_pause_flip > 100 and not gamestate.is_paused:
            gamestate.is_paused = True
            self.last_pause_flip = self.real_game_time
        if keys[pygame.K_p] and self.real_game_time - self.last_pause_flip > 100 and gamestate.is_paused:
            gamestate.is_paused = False
            self.last_music_flip = self.real_game_time

        # On décompte le temps total de pause
        self.game_is_paused_this_frame = gamestate.is_paused
        if not self.game_was_paused_last_frame and self.game_is_paused_this_frame:
            self.last_pause_start = now
        if not self.game_is_paused_this_frame and self.game_was_paused_last_frame:
            self.last_pause_end = now
            self.total_pause_time += self.last_pause_end - self.last_pause_start

    def update_frame(self):
        # Récupération des évènements principalement est-ce qu'une touche du clavier a été pressée
        event_list = pygame.event.get()

        # Récupération des infos souris
        mouse_pos = pygame.mouse.get_pos() - camera_group.offset
        mouse_keys = pygame.mouse.get_pressed(3)

        # Récupération des touches pressées
        keys = pygame.key.get_pressed()

        # Récupération de l'heure exacte
        now = pygame.time.get_ticks()

        # Décompte du temps de pause
        self.update_pause(now, keys)

        # Calcul du temps effectif écoulé
        self.real_game_time = now - self.total_pause_time
        #print("Time : ", now - self.real_game_time, gamestate.is_paused)

        # Gestion du spawn des monstres
        self.update_mob_spawn()

        # Gestion des menus + tutoriels, ça devrait sûrement être ailleurs
        self.draw_menus(now, event_list, keys)

        # Gestion des changements de musique
        self.update_music(keys)

        

        # Gestion des déplacements du héros
        hero.move(keys)
        
        # Affichage du jeu
        if self.game_has_started:
            gamestate.drawGame(mouse_pos)

        # Update de la logique du jeu
        if not gamestate.is_paused and self.game_has_started:
            update_game(keys, mouse_pos, mouse_keys, self.real_game_time)
        gamestate.buttons.update(camera_group)

        # Quitter le jeu ; attention cela n'exporte pas le score...
        if keys[pygame.K_ESCAPE]:
            return False

        # Contrôle du nombre de fps (ne marche pas très bien)
        clock.tick_busy_loop(gamestate.fps)
        
        return True