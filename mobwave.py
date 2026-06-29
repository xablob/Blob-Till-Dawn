import numpy as np
import pygame

from enemy import Enemy
from game_init import gamestate
from gamestate import dimx, dimy

waves = pygame.sprite.Group()

mob_dispersion = 100
mob_pack_dispersion = 100

hero = gamestate.hero


class MobWave(pygame.sprite.Sprite):
    def __init__(self, number_of_mobs, call_time):
        pygame.sprite.Sprite.__init__(self, gamestate.mobwaves)
        self.number_of_mobs_to_spawn = int(number_of_mobs)
        self.call_time = call_time
        self.spawn_times = [
            self.call_time + 1500 * (1 - id_mob / self.number_of_mobs_to_spawn) ** 4
            for id_mob in range(self.number_of_mobs_to_spawn)
        ]  # delay some spawns to avoid big lag on 1 frame
        alpha = np.random.uniform(0, 2 * np.pi)
        self.coordinates = [
            hero.rect.centerx + np.cos(alpha) * dimx / 2,
            hero.rect.centery + np.sin(alpha) * dimy / 2,
        ]
        # self.coordinates = [960, 540]
        self.number_of_mobs_spawned = 0
        waves.add(self)

    def update(self, real_game_time):
        date = real_game_time
        if self.number_of_mobs_to_spawn <= 0:
            self.kill()
        index_to_remove = []
        for i in range(int(self.number_of_mobs_to_spawn)):
            if date > self.spawn_times[i]:
                enemy = Enemy(date)
                enemy.rect.x = self.coordinates[0] + np.random.uniform(
                    -mob_pack_dispersion, mob_pack_dispersion
                )
                enemy.rect.y = self.coordinates[1] + np.random.uniform(
                    -mob_pack_dispersion, mob_pack_dispersion
                )
                self.number_of_mobs_to_spawn -= 1
                index_to_remove.append(i)

        for index in index_to_remove[::-1]:
            self.spawn_times.pop(index)
