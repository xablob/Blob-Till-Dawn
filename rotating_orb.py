import numpy as np
import pygame

from spritesheet import SpriteSheet
from target_tag import TagList, TargetTag
from utilities import get_angle, reshape

base_angular_velocity = 2 * np.pi / 180

energyball_spritesheet = SpriteSheet("Assets/ball.png")

rotating_orb_image = reshape(
    pygame.image.load("Assets/Fireball/fireballupdown.png").convert_alpha(), 2
)

energyball_image = energyball_spritesheet.image_at((0, 0, 100, 100)).convert_alpha()
energyball_image.set_colorkey((0, 0, 0))
energyball_image = reshape(energyball_image, 2)
energyball_image.set_colorkey((0, 0, 0))
energyball_image = energyball_image.convert_alpha()

# rotating_orb_image = energyball_image


class RotatingOrb(pygame.sprite.Sprite):
    def __init__(
        self,
        gamestate,
        radius,
        angle,
        duration=False,
        circular_direction=1,
        angular_velocity_multiplier=1,
        offset_angle=0,
        base_damage=5,
    ):
        super().__init__(gamestate.camera_group, gamestate.hero.rotating_orbs)
        self.angle = angle + offset_angle
        offset_x = radius * np.cos(self.angle)
        offset_y = radius * np.sin(self.angle)
        self.gamestate = gamestate
        self.radius = radius
        self.initial_angle = self.angle
        self.hero = gamestate.hero
        self.hero.has_rotating_orbs = True
        self.image = rotating_orb_image
        self.orig_image = rotating_orb_image
        self.offset_angle = offset_angle
        self.angular_velocity_multiplier = angular_velocity_multiplier
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rotate_angle = get_angle((offset_x, -offset_y)) * 180 / np.pi
        self.image = pygame.transform.rotate(self.orig_image, self.rotate_angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.hero.rect.centerx + offset_x
        self.rect.centery = self.hero.rect.centery + offset_y
        self.direction = (5, 0)
        self.base_damage = base_damage
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction_vector = np.zeros([2])
        self.offset = pygame.math.Vector2(0, 0)
        self.skills = ["bonk"]
        self.cooldown = 200
        self.date_of_last_attack = -9999
        self.current_time = gamestate.time
        self.spawn_date = self.current_time
        self.potential_targets = gamestate.enemies_group
        self.circular_direction = circular_direction
        self.angular_velocity = angular_velocity_multiplier * base_angular_velocity
        self.duration = duration
        self.tag_list = TagList()

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def update(self):
        self.current_time = self.gamestate.time
        self.tag_list.update(self.current_time)
        if self.duration:
            if self.current_time - self.spawn_date > self.duration:
                self.kill()
        if self.hero.unhinged_orbs:
            pass
        for entity in self.potential_targets.sprites():
            if self.is_colliding_with(entity) and self.tag_list.does_not_contain(entity):
                entity.life -= self.base_damage
                if entity.life <= 0:
                    entity.part_vers_une_destination_mystérieuse(self.hero)
                    self.hero.kills += 1
                else:
                    TargetTag(self.current_time, self, entity)
        self.rect.centerx += self.hero.delta_position[0]
        self.rect.centery += self.hero.delta_position[1]
        angle = get_angle(
            (
                self.rect.centerx - self.hero.rect.centerx,
                self.rect.centery - self.hero.rect.centery,
            )
        )
        # random_var = np.random.randint(1, 7)*np.pi/180
        angle -= self.circular_direction * self.angular_velocity
        self.rect.centerx = self.hero.rect.centerx + self.radius * np.cos(angle)
        self.rect.centery = self.hero.rect.centery + self.radius * np.sin(angle)
        self.image = pygame.transform.rotate(self.orig_image, self.rotate_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        # self.rotate_angle += random_var*180/np.pi
        self.rotate_angle += self.circular_direction * 180 * self.angular_velocity / np.pi
        self.rotate_angle = self.rotate_angle % 360
