import numpy as np
import pygame

from music import fireball_sound
from spritesheet import SpriteSheet
from target_tag import TagList, TargetTag
from utilities import get_angle, reshape

energyball_spritesheet = SpriteSheet("Assets/ball.png")


coeff_dispersion = 4

merge_radius = 200

multiproj_source_deviation = 50

second = 1000  # milliseconds

cooldowns_table = {"Fireball": 1000}
attack_coeff_table = {"Fireball": 1}
sound_table = {"Fireball": fireball_sound}

entity_targeted_projectiles = pygame.sprite.Group()


class ProjectileSkill:
    def __init__(self, gamestate, name, projectile_type, image):
        self.name = name
        self.projectile_type = projectile_type
        self.image = image
        self.cooldown = cooldowns_table[self.name]
        self.sound = sound_table[self.name]
        self.chains = 3
        self.gamestate = gamestate

    def activate(self, target, source):
        pygame.mixer.Sound.play(self.sound)
        if self.projectile_type == "Skillshot":
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
                angles = [
                    i * 2 * np.pi / source.number_of_proj for i in range(source.number_of_proj)
                ]
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
                final_direction = [np.cos(angle), np.sin(angle)]
                Skillshot(
                    self.gamestate,
                    final_direction,
                    angle,
                    source,
                    self.name,
                    self.image,
                    source.projectile_duration,
                    source.projectile_speed,
                    0,
                    source.offset_radius,
                )


Skillshots = pygame.sprite.Group()


class Skillshot(pygame.sprite.Sprite):
    def __init__(
        self,
        gamestate,
        direction,
        angle,
        source,
        skill_name,
        image,
        duration,
        projectile_speed,
        sequential_offset=0,
        offset_radius=0,
        taglist=False,
        has_split=False,
    ):
        super().__init__(Skillshots, gamestate.camera_group.projectiles)
        self.source = source
        self.angle = angle
        self.skill_name = skill_name
        self.original_image = image
        self.sequential_offset = sequential_offset

        self.image = image
        self.has_taken_a_portal = False
        self.attack_power = attack_coeff_table[self.skill_name]
        self.direction = direction
        self.gamestate = gamestate

        native_chains = 1
        self.number_of_chains = native_chains + source.number_of_chains

        self.projectile_type = "Entity targeted projectile"
        self.source = source
        self.potential_targets = source.potential_targets

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.centerx = self.source.rect.centerx + offset_radius * np.cos(self.angle)
        self.rect.centery = self.source.rect.centery + offset_radius * np.sin(self.angle)
        self.projectile_speed = source.projectile_speed
        self.spawn_date = pygame.time.get_ticks()
        self.duration = duration
        self.pierce = False
        self.expiration_date = self.spawn_date + self.duration
        self.direction_vector = (
            self.projectile_speed * np.array(self.direction) / np.linalg.norm(self.direction)
        )
        self.target_dead = False
        self.already_hit_entities = pygame.sprite.Group()
        self.remaining_chains = self.number_of_chains
        self.current_time = self.spawn_date
        self.has_split = has_split
        self.offset_radius = offset_radius
        if not taglist:
            self.tag_list = TagList()
        else:
            self.tag_list = taglist
        if sequential_offset == 0:
            for sequential_proj in range(source.sequential_number_of_proj - self.sequential_offset):
                projectile = Skillshot(
                    gamestate,
                    self.direction,
                    self.angle,
                    self.source,
                    self.skill_name,
                    self.image,
                    self.duration,
                    self.projectile_speed,
                    self.sequential_offset + sequential_proj + 1,
                    offset_radius,
                    self.tag_list,
                )
                projectile.rect.centerx = (
                    self.rect.centerx + self.direction_vector[0] * 4 * projectile.sequential_offset
                )
                projectile.rect.centery = (
                    self.rect.centery + self.direction_vector[1] * 4 * projectile.sequential_offset
                )

    def copy(self, offset):
        new_proj = Skillshot(
            self.gamestate,
            self.direction,
            self.angle,
            self.source,
            self.skill_name,
            self.image,
            self.duration,
            self.projectile_speed,
            1,
            self.offset_radius,
            self.tag_list,
            self.has_split,
        )
        new_proj.rect.center = self.rect.center
        new_proj.rect.centerx += offset[0]
        new_proj.rect.centery += offset[1]
        new_proj.spawn_data = self.spawn_date
        new_proj.has_taken_a_portal = True
        new_proj.projectile_speed = self.projectile_speed
        new_proj.pierce = self.pierce

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def apply_to(self, target):
        TargetTag(self.current_time, self, target)
        damage = self.source.attack_power * self.attack_power
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
        if not self.has_split:
            for _ in range(self.source.number_of_splits):
                angle = np.random.uniform(0, 2 * np.pi)
                direction = [np.cos(angle), np.sin(angle)]
                split_proj = Skillshot(
                    self.gamestate,
                    direction,
                    angle,
                    self.source,
                    self.skill_name,
                    self.image,
                    self.duration,
                    self.projectile_speed,
                    -1,
                    self.offset_radius,
                    self.tag_list,
                    True,
                )
                split_proj.rect.center = target.rect.center
            self.has_split = True

    def generate_random_direction(self):
        angle = np.random.uniform(0, 2 * np.pi)
        new_x = self.rect.centerx + 100000 * np.cos(angle)
        new_y = self.rect.centery + 100000 * np.sin(angle)
        self.target_coordinates = [new_x, new_y]

    def update(self, time):
        self.tag_list.update(time)
        self.direction_vector = (
            self.projectile_speed * np.array(self.direction) / np.linalg.norm(self.direction)
        )
        self.current_time = time
        self.tag_list.update(self.current_time)
        if (self.current_time - self.spawn_date) / 1000 > self.duration:
            self.kill()
        for target in self.potential_targets.sprites():
            if self.is_colliding_with(target) and self.tag_list.does_not_contain(target):
                self.apply_to(target)
                if not self.pierce:
                    self.kill()
        for obstacle in self.gamestate.obstacles:
            if self.is_colliding_with(obstacle):
                self.apply_to(obstacle)
        self.rect.centerx += self.direction_vector[0]
        self.rect.centery += self.direction_vector[1]
        # self.max_change = max(abs(self.direction_vector[0]), abs(self.direction_vector[1]))
        # rotation_angle = get_angle(self.direction_vector)
        # print("angle = ", rotation_angle*180/np.pi)
        # self.image, self.rect = rotate(self.original_image, self.rect, rotation_angle)
        # if self.max_change == abs(self.direction_vector[0]):
        #     if self.direction_vector[0] >= 0:
        #         self.image = self.right_to_left_image
        #     else:
        #         self.image = self.left_to_right_image
        # else:
        #     assert self.max_change == abs(self.direction_vector[1]), "Big problem"
        #     if self.direction_vector[1] >= 0:
        #         self.image = self.up_to_down_image
        #     else:
        #         self.image = self.down_to_up_image


coeff_reshape = 2

energyball_image = energyball_spritesheet.image_at((0, 0, 100, 100)).convert_alpha()
energyball_image.set_colorkey((0, 0, 0))
energyball_image = reshape(energyball_image, 2)
energyball_image.set_colorkey((0, 0, 0))
energyball_image = energyball_image.convert_alpha()

fireball_image_EW, fireball_image_NS = energyball_image, energyball_image
water_orb_image = reshape(pygame.image.load("Assets/Water__05.png").convert_alpha(), 2.2)
arcane_orb_image = reshape(pygame.image.load("Assets/Arcane_Effect_7.png").convert_alpha(), 2)
# fireball_image = arcane_orb_image
# fireball_image = water_orb_image
fireball_image = water_orb_image
