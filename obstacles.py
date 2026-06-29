import pygame

from game_init import camera_group, gamestate
from utilities import replace_outside_obstacle, reshape

dimx = 1920
dimy = 1080


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, coeff=1):
        super().__init__(camera_group.map_objects, gamestate.obstacles)
        self.image = reshape(
            pygame.image.load("Assets/Obstacle/mountain_landscape.PNG").convert_alpha(), coeff
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.offset = pygame.math.Vector2(0, 0)
        self.id = "not an entity"
        self.type = "Obstacle"
        self.is_destructible_obstacle = False
        self.is_obstacle = True

    def update(self, time):
        for entity in gamestate.hero_group.sprites():
            if entity.is_colliding_with(self):
                replace_outside_obstacle(self, entity)
        for entity in gamestate.enemies_group.sprites():
            if not entity.is_obstacle:
                if entity.is_colliding_with(self):
                    replace_outside_obstacle(self, entity)
        for entity in gamestate.boss_group.sprites():
            if entity.is_colliding_with(self):
                replace_outside_obstacle(self, entity)


class EnemyObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, coeff=1):
        super().__init__(camera_group, gamestate.obstacles, gamestate.enemies_group)
        self.image = reshape(
            pygame.image.load("Assets/Obstacle/mountain_landscape.PNG").convert_alpha(), coeff
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.offset = pygame.math.Vector2(0, 0)
        self.id = "enemy obstacle"
        self.type = "Obstacle"
        self.life = 40
        self.max_life = self.life
        self.is_obstacle = True
        self.bool_draw_health = True
        self.is_destructible_obstacle = True

    def update(self, time):
        self.offset = camera_group.offset
        for entity in gamestate.hero_group.sprites():
            if entity.is_colliding_with(self):
                replace_outside_obstacle(self, entity)
        for entity in gamestate.enemies_group.sprites():
            if not entity.is_obstacle:
                if entity.is_colliding_with(self):
                    replace_outside_obstacle(self, entity)
        for entity in gamestate.boss_group.sprites():
            if entity.is_colliding_with(self):
                replace_outside_obstacle(self, entity)

    def draw_health(self, surf, pos=False):
        health_rect = pygame.Rect(0, 0, self.image.get_width(), 7)
        health_rect.midbottom = self.rect.centerx, self.rect.top
        health_rect.topleft += self.offset
        if not pos:
            draw_health_bar(
                surf,
                health_rect.topleft,
                health_rect.size,
                (0, 0, 0),
                (255, 0, 0),
                (0, 255, 0),
                self.life / self.max_life,
            )
        else:
            draw_health_bar(
                surf,
                (dimx / 2, 40),
                health_rect.size,
                (0, 0, 0),
                (255, 0, 0),
                (0, 255, 0),
                self.life / self.max_life,
            )

    def part_vers_une_destination_mystérieuse(self, source):
        self.kill()


def draw_health_bar(surf, pos, size, borderC, backC, healthC, progress):
    pygame.draw.rect(surf, backC, (*pos, *size))
    pygame.draw.rect(surf, borderC, (*pos, *size), 1)
    innerPos = (pos[0] + 1, pos[1] + 1)
    innerSize = ((size[0] - 2) * progress, size[1] - 2)
    rect = (
        round(innerPos[0]),
        round(innerPos[1]),
        round(innerSize[0]),
        round(innerSize[1]),
    )
    pygame.draw.rect(surf, healthC, rect)
