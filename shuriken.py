import numpy as np
import pygame

from target_tag import TagList, TargetTag
from utilities import get_angle, reshape

shuriken_image1 = reshape(pygame.image.load("Assets/shuriken_1.png").convert_alpha(), 4)
shuriken_image2 = reshape(pygame.image.load("Assets/shuriken_2.png").convert_alpha(), 4)
shuriken_image3 = reshape(pygame.image.load("Assets/shuriken_3.png").convert_alpha(), 4)
shuriken_image4 = reshape(pygame.image.load("Assets/shuriken_4_blue.png").convert_alpha(), 4.5)
shuriken_image5 = reshape(pygame.image.load("Assets/shuriken_4_purple.png").convert_alpha(), 4.5)
shuriken_image6 = reshape(pygame.image.load("Assets/shuriken_4.png").convert_alpha(), 4.5)

shuriken_images = [shuriken_image1, shuriken_image2, shuriken_image3]

shuriken_sound = pygame.mixer.Sound("Assets/Music/sword sound.wav")
shuriken_sound.set_volume(0.08)


class Shuriken(pygame.sprite.Sprite):
    def __init__(
        self,
        gamestate,
        direction,
        angle,
        source,
        taglist=False,
    ):
        super().__init__(gamestate.shurikens, gamestate.camera_group.projectiles)
        self.source = source
        self.gamestate = gamestate
        self.source.shuriken_ammo -= 1
        self.angle = angle
        self.skill_name = "Shuriken"
        self.original_image = shuriken_images[np.random.randint(0, 3)]
        self.original_image = shuriken_image6
        self.image = self.original_image
        self.attack_power_coefficient = 0.5  # coefficient that multiplies the source's attack power
        self.direction = direction

        self.projectile_type = "Shuriken"

        self.source = source
        self.potential_targets = source.potential_targets

        self.rect = self.image.get_rect()
        offset_radius = 5
        self.rect.centerx = self.source.rect.centerx + offset_radius * np.cos(self.angle)
        self.rect.centery = self.source.rect.centery + offset_radius * np.sin(self.angle)
        self.projectile_speed = 8
        self.original_projectile_speed = self.projectile_speed
        self.spawn_date = gamestate.time
        self.duration = 1000
        self.pierce = True
        self.expiration_date = self.spawn_date + 15 * self.duration
        self.direction_vector = (
            self.projectile_speed * np.array(self.direction) / np.linalg.norm(self.direction)
        )
        self.target_dead = False
        self.already_hit_entities = pygame.sprite.Group()
        self.current_time = self.spawn_date
        self.rotation_angle = 0

        if not taglist:
            self.tag_list = TagList()
        else:
            self.tag_list = taglist
        self.has_turned = False

        self.catch_radius = 80

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def apply_to(self, target):
        TargetTag(self.current_time, self, target)
        damage = self.source.attack_power * self.attack_power_coefficient
        if not target.is_obstacle:
            target.life -= damage
            if target.life <= 0:
                target.part_vers_une_destination_mystérieuse(self.source)
                self.source.kills += 1
        if target.is_obstacle:
            if target.is_destructible_obstacle:
                target.life -= damage * self.source.coeff_object_damage
                if target.life <= 0:
                    target.part_vers_une_destination_mystérieuse(self.source)
            self.kill()

    def generate_random_direction(self):
        angle = np.random.uniform(0, 2 * np.pi)
        new_x = self.rect.centerx + 100000 * np.cos(angle)
        new_y = self.rect.centery + 100000 * np.sin(angle)
        self.target_coordinates = [new_x, new_y]

    def returns(self):
        self.direction = [
            self.source.rect.centerx - self.rect.centerx,
            self.source.rect.centery - self.rect.centery,
        ]
        self.angle = get_angle(self.direction)
        self.image = shuriken_image5
        self.has_turned = True

    def distance(self, entity):
        return (
            (self.rect.centerx - entity.rect.centerx) ** 2
            + (self.rect.centery - entity.rect.centery) ** 2
        ) ** 0.5

    def update(self, time):
        self.tag_list.update(time)
        self.direction_vector = self.projectile_speed * np.array(
            [np.cos(self.angle), np.sin(self.angle)]
        )
        self.angle += self.rotation_angle * np.pi / 180
        self.current_time = time
        self.projectile_speed = abs(
            1.75
            * (1 - ((self.current_time - self.spawn_date) / self.duration))
            * self.original_projectile_speed
        )
        self.tag_list.update(self.current_time)
        if self.current_time - self.spawn_date > self.duration and self.has_turned == False:
            self.returns()
        if self.current_time > self.expiration_date:
            self.kill()
        for target in self.potential_targets.sprites():
            if self.is_colliding_with(target) and self.tag_list.does_not_contain(target):
                self.apply_to(target)
                if not self.pierce:
                    self.kill()
        for obstacle in self.gamestate.obstacles:
            if self.is_colliding_with(obstacle):
                self.apply_to(obstacle)
        if self.has_turned == True:
            if self.distance(self.source) < self.catch_radius:
                self.source.shuriken_ammo += 1
                self.kill()
        self.rect.centerx += self.direction_vector[0]
        self.rect.centery += self.direction_vector[1]


class ShurikenSkill:
    def __init__(self, gamestate):
        self.name = "Shuriken"
        self.projectile_type = "Shuriken"
        self.sound = shuriken_sound
        self.gamestate = gamestate

    def activate(self, target, source):
        pygame.mixer.Sound.play(self.sound)
        if target == False:
            random_angle = np.random.uniform(0, 2 * np.pi)
            radius = 500  # to avoid edge cases due to hitboxes etc
            target_pos = [
                source.rect.centerx + radius * np.cos(random_angle),
                source.rect.centery + radius * np.sin(random_angle),
            ]
        else:
            if not type(target) == pygame.math.Vector2:
                target_pos = (target.rect.centerx, target.rect.centery)
            else:
                target_pos = target
        direction = [
            target_pos[0] - source.rect.centerx,
            target_pos[1] - source.rect.centery,
        ]
        angle_base = get_angle(direction)
        if source.angle_range == "All directions":
            angles = [i * 2 * np.pi / source.number_of_proj for i in range(source.number_of_proj)]
        else:
            dispersion_max = (np.pi / 2) * (1 - 1 / source.number_of_proj) ** 2
            angles = np.linspace(-dispersion_max, dispersion_max, source.number_of_proj)
        for index_proj in range(1, source.number_of_proj + 1):
            # angle = angle_base + np.pi/2 - index_proj*np.pi/(source.number_of_proj + 1)
            coeff_dispersion = source.number_of_proj
            angle = (
                angle_base
                + np.pi * (coeff_dispersion - 2) / (2 * coeff_dispersion)
                - index_proj
                * np.pi
                / (source.number_of_proj + 1)
                * (coeff_dispersion - 2)
                / coeff_dispersion
            )
            angle = angle_base + angles[index_proj - 1]
            Shuriken(
                self.gamestate,
                direction,
                angle,
                source,
                taglist=False,
            )
