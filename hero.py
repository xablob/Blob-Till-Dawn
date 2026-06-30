import numpy as np
import pygame
import requests

from button import Button
from camera import check_for_obstacles
from map_objects import tp_anim
from music import ghost_sound, tp_sound
from params import (
    coeff_resize_x,
    coeff_resize_y,
    color_period,
    dimx,
    gold_color,
    xp_bar_height,
    xp_bar_length,
    xp_bar_topleft_x,
    xp_bar_topleft_y,
    xp_color,
)
from projectile import ProjectileSkill, fireball_image
from rotating_orb import RotatingOrb
from shuriken import ShurikenSkill
from utilities import reshape

pickup_cooldown = 1000

buff_text_color = (255, 255, 255)
coeff_petit = 9 * np.sqrt(2)

auto_attack = True


insta_levelup = False


class Hero(pygame.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, gamestate):
        # Call the parent class (Sprite) constructor
        super().__init__(gamestate.camera_group, gamestate.hero_group)
        gamestate.hero = self
        self.gamestate = gamestate

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.non_flip_image = reshape(
            pygame.image.load("Assets/FluffyBlob/CharFluffyBlue.png").convert_alpha(),
            coeff_petit,
        )
        self.flip_image = reshape(
            pygame.transform.flip(
                pygame.image.load("Assets/FluffyBlob/CharFluffyBlue.png").convert_alpha(),
                True,
                False,
            ),
            coeff_petit,
        )

        self.image = self.flip_image

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        gamestate.hero = self
        poly_size = 100
        #Polygon_effect(self, np.array([(0, 0), (100, 0), (0, 100), (-50, 150), (50, 375)]), rotation_speed= 5*np.pi/180)
        #Polygon_effect(self, np.array([(-poly_size, -poly_size), (poly_size, -poly_size), (poly_size, poly_size), (-poly_size, poly_size)]), width = 10, rotation_speed= 0.04*np.pi)
        #Polygon_effect(self.gamestate, self, [(-poly_size, 2*poly_size), (3*poly_size, poly_size), (-2*poly_size, -3*poly_size)])
        self.rect = self.image.get_rect()
        self.level = 1
        self.xp = 0
        self.type = "Hero"
        self.name = "Xavier"
        self.rect.centerx = 0
        self.rect.centery = 0
        self.flip = False
        self.type = "entity"
        self.last_portal_spawn = -999999999999999
        self.portal_spawn_cooldown = 500
        self.portal_tp_cooldown = 10000
        self.last_portal_tp = -9999999
        self.direction = 1
        self.direction_vector = np.zeros([2])
        self.velocity = 4
        self.original_velocity = self.velocity
        self.auto_skills = {
            "Fireball": ProjectileSkill(gamestate, "Fireball", "Skillshot", fireball_image)
        }
        self.cooldowns = {}
        self.initial_cooldowns = {}
        self.sequential_number_of_proj = 0
        self.number_of_proj = 1
        self.angle_range = "In front"
        self.mouse_attack_cooldown = 300
        self.last_mouse_attack = -999999999999
        self.date_of_last_attack = {}
        self.tp_distance = 50
        for skill in self.auto_skills.values():
            self.cooldowns[skill.name] = skill.cooldown
            self.initial_cooldowns[skill.name] = skill.cooldown
            self.date_of_last_attack[skill.name] = -9999
        self.current_time = 0
        self.life = 150
        self.max_life = self.life
        self.original_max_life = self.max_life
        self.attack_power = 25  # 25 for playable value
        #self.attack_power = 400 # boss test value
        self.initial_attack_power = self.attack_power
        self.projectile_speed = 15
        self.projectile_duration = 10
        self.kills = 0
        self.id = "Le goat"
        self.number_of_chains = 3
        self.offset = pygame.math.Vector2(0, 0)
        self.last_pickup = -99999999999999
        self.potential_targets = gamestate.enemies_group
        self.last_tp = -99999999
        self.tp_cooldown = 2000
        self.rewind_window = 5000
        self.last_rewind = -99999
        self.rewind_cooldown = 20000
        self.time_rewind = False
        self.has_rotating_orbs = False
        self.offset_radius = 0
        self.rotating_orbs = pygame.sprite.Group()
        self.delta_position = (0, 0)
        self.last_orbs_buff = -9999999
        self.orbs_buff_cooldown = 20000
        self.orbs_buff_duration = 10000
        self.orb_level = 0
        self.unhinged_orbs = False
        self.forever_lost_life = 0
        self.number_of_splits = 0
        self.current_level = 1

        # self.levels_xp_thresholds = [xp_threshold*i for i in range(max_level + 1)]
        # self.total_xp_necessary_per_level = [sum([self.levels_xp_thresholds[i] for i in range(level)]) for level in range(1, max_level + 1)]
        self.total_xp_necessary_per_level = [
            2,
            3,
            4,
            5,
            7,
            9,
            11,
            14,
            17,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            60,
            70,
            80,
            100,
        ]
        # self.total_xp_necessary_per_level = [0, 3, 4, 5, 7, 9, 11, 14, 17, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100]
        self.max_level = len(self.total_xp_necessary_per_level)
        # print(self.total_xp_necessary_per_level)
        self.next_total_xp_necessary = self.total_xp_necessary_per_level[self.current_level]
        self.last_total_xp = 0
        self.is_obstacle = False

        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery

        self.coeff_object_damage = 0.005

        self.shuriken_ammo = 2
        self.max_shuriken_ammo = self.shuriken_ammo + 1
        self.shuriken_ammo_cooldown = 8000
        self.last_shuriken_ammo_refund = -4000
        self.shuriken_throw_cooldown = 500
        self.last_shuriken_throw = -99999999

        self.HeroShurikenSkill = ShurikenSkill(gamestate)

        self.skill_ranks = {"Bulles" : 1, "Rotating Orbs" : 0, "Shuriken" : 1}

    def drop_items(self):
        pass

    def add_xp(self, xp_value):
        self.xp += xp_value
        if self.current_level <= self.max_level:
            if self.xp - self.last_total_xp >= self.next_total_xp_necessary or insta_levelup:
                self.level_up()

    def update_skills(self):
        pass

    def level_up(self):
        self.gamestate.is_paused = True
        self.current_level += 1
        if self.current_level < self.max_level:
            self.next_total_xp_necessary = self.total_xp_necessary_per_level[self.current_level]
            self.last_total_xp += self.total_xp_necessary_per_level[self.current_level - 1]
        button_offset_x = 200 * coeff_resize_x
        button_offset_y = 200 * coeff_resize_y
        button_width = 350 * coeff_resize_x
        button_height = 700 * coeff_resize_y
        ghost_sound.play()
        levelup_buttons = pygame.sprite.Group()
        Button(
            self.gamestate,
            button_offset_x,
            button_offset_y,
            button_width,
            button_height,
            self.gamestate.camera_group,
            self,
            levelup_buttons,
        )
        Button(
            self.gamestate,
            dimx / 2 - button_width / 2,
            button_offset_y,
            button_width,
            button_height,
            self.gamestate.camera_group,
            self,
            levelup_buttons,
        )
        Button(
            self.gamestate,
            dimx - button_offset_x - button_width,
            button_offset_y,
            button_width,
            button_height,
            self.gamestate.camera_group,
            self,
            levelup_buttons,
        )

        # gamestate.hero_is_not_paused = True

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def upgrade_orbs(self):
        if self.orb_level == 0:
            self.create_rotating_orbs()
        elif self.orb_level == 1:
            self.create_rotating_orbs(4, 300, False, 1, 2, np.pi / 4, base_damage=10)
        elif self.orb_level == 2:
            self.create_rotating_orbs(8, 500, False, -1, 2, 0, 5)
        elif self.orb_level == 3:
            for orb in self.rotating_orbs:
                RotatingOrb(
                    self.gamestate,
                    orb.radius,
                    orb.angle,
                    orb.duration,
                    orb.circular_direction,
                    2 * orb.angular_velocity_multiplier,
                    np.pi / 4,
                    orb.base_damage * 0.25,
                )
                orb.angular_velocity = 2 * orb.angular_velocity

    def create_rotating_orbs(
        self,
        n_orbs=4,
        radius=200,
        duration=False,
        circular_direction=1,
        angular_velocity_multiplier=1,
        offset_angle=0,
        base_damage=5,
    ):
        for i in range(n_orbs):
            angle = i * 2 * np.pi / n_orbs
            RotatingOrb(
                self.gamestate,
                radius,
                angle,
                duration,
                circular_direction,
                angular_velocity_multiplier,
                offset_angle,
                base_damage,
            )

    def distance(self, sprite):
        return (
            (self.rect.centerx - sprite.rect.centerx) ** 2
            + (self.rect.centery - sprite.rect.centery) ** 2
        ) ** 0.5

    def part_vers_une_destination_mystérieuse(
        self, source):
        print("R I P")
        for orb in self.rotating_orbs:
            orb.kill()
        self.gamestate.last_hero_coordinates = self.rect.center
        self.export_score()
        self.kill()
        self.gamestate.end_game()
        

    def reset_orbs(self):
        for orb in self.rotating_orbs.sprites():
            RotatingOrb(
                self.gamestate,
                orb.radius,
                orb.initial_angle,
                orb.duration,
                orb.circular_direction,
                orb.angular_velocity_multiplier,
                orb.offset_angle,
                orb.base_damage,
            )
            orb.kill()

    def export_score(self):
        request_name = (
            str("http://dreamlo.com/lb/-t8Yvx3h5UWD7cLFhThYIgcKEY90PwAUmXNOpxPY3Nzw/add/")
            + str(self.leaderboard_name)
            + "/"
            + str(self.kills)
        )
        requests.post(request_name)

    def find_nearest_target(self):
        min_distance = 99999
        target = False
        success = False
        for entity in self.potential_targets.sprites():
            current_distance = self.distance(entity)
            if current_distance < min_distance:
                target = entity
                min_distance = current_distance
                success = True
        return success, target

    def attack(self, keys, mouse_pos, mouse_keys):
        target = False
        success, target = self.find_nearest_target()
        # if mouse_keys[0]:
        #     if self.current_time - self.last_mouse_attack > self.mouse_attack_cooldown:
        #         self.auto_skills["Fireball"].activate(mouse_pos, self)
        #         self.last_mouse_attack = self.current_time
        # if mouse_keys[2] or keys[pygame.K_a]:
        #     if self.current_time - self.last_portal_spawn > self.portal_spawn_cooldown:
        #         portal_already_exist = False
        #         for portal in gamestate.portals:
        #             if portal.rect.centerx == mouse_pos[0] and portal.rect.centery == mouse_pos[1]:
        #                 portal_already_exist = True
        #         if not portal_already_exist:
        #             Portal(mouse_pos)
        #             if len(portals.sprites()) > 4:
        #                 oldest_portal_age = -99999999
        #                 oldest_portal = None
        #                 for portal in portals.sprites():
        #                     portal_age = self.current_time - portal.spawn_date
        #                     if portal_age > oldest_portal_age:
        #                         oldest_portal = portal
        #                         oldest_portal_age = portal_age
        #                 oldest_portal.kill()
        #             self.last_portal_spawn = self.current_time
        if success and auto_attack:
            for skill in self.auto_skills.values():
                if (
                    self.current_time - self.date_of_last_attack[skill.name]
                    > self.cooldowns[skill.name]
                ):
                    skill.activate(target, self)
                    self.date_of_last_attack[skill.name] = self.current_time
        if (
            self.shuriken_ammo > 0
            and self.current_time - self.last_shuriken_throw > self.shuriken_throw_cooldown
        ):
            self.HeroShurikenSkill.activate(target, self)
            self.last_shuriken_throw = self.current_time

        # if keys[pygame.K_a]:
        #     if self.current_time - self.date_of_last_attack["Tomato trap"] > self.cooldowns["Tomato trap"]:
        #         self.on_use_skills["Tomato trap"].activate(mouse_pos, self)
        #         self.date_of_last_attack["Tomato trap"] = self.current_time

    def draw_health(self, surf):
        health_rect = pygame.Rect(
            0,
            0,
            2 * self.image.get_width() * self.max_life / self.original_max_life,
            18,
        )
        health_rect.topleft = self.rect.topleft + pygame.math.Vector2(-30, -25)
        health_rect.topleft += self.offset
        draw_health_bar(
            surf,
            health_rect.topleft,
            health_rect.size,
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            self.life / self.max_life,
        )
        rect = pygame.Rect(
            0,
            0,
            2 * self.image.get_width() * self.forever_lost_life / self.original_max_life,
            18,
        )
        rect.topleft = health_rect.topright
        pygame.draw.rect(surf, (75, 0, 130), rect)

    def draw_xp(self, surf):
        pygame.draw.rect(
            surf,
            (0, 0, 0),
            pygame.Rect(xp_bar_topleft_x, xp_bar_topleft_y, xp_bar_length, xp_bar_height),
        )
        if self.current_level < self.max_level:
            pygame.draw.rect(
                surf,
                xp_color,
                pygame.Rect(
                    xp_bar_topleft_x,
                    xp_bar_topleft_y,
                    xp_bar_length * (self.xp - self.last_total_xp) / (self.next_total_xp_necessary),
                    xp_bar_height,
                ),
            )
            # pygame.draw.rect(surf, (200*abs(np.sin(self.current_time/color_period)), 0, 255*abs(np.sin(np.pi/4 + self.current_time/color_period))), pygame.Rect(xp_bar_topleft_x, xp_bar_topleft_y, xp_bar_length*(self.xp - self.last_total_xp)/(self.next_total_xp_necessary - self.last_total_xp), xp_bar_height))
        else:
            pygame.draw.rect(
                surf,
                (0, 0, max(50, 120 * abs(np.sin(self.current_time / color_period)))),
                pygame.Rect(xp_bar_topleft_x, xp_bar_topleft_y, xp_bar_length, xp_bar_height),
            )
            # pygame.draw.rect(surf, (200*abs(np.sin(self.current_time/color_period)), 0, 255*abs(np.sin(np.pi/4 + self.current_time/color_period))), pygame.Rect(xp_bar_topleft_x, xp_bar_topleft_y, xp_bar_length, xp_bar_height))
        for i in range(11):
            pygame.draw.line(
                surf,
                gold_color,
                (xp_bar_topleft_x + i * xp_bar_length / 10, xp_bar_topleft_y),
                (xp_bar_topleft_x + i * xp_bar_length / 10, xp_bar_topleft_y + xp_bar_height),
                2,
            )
        pygame.draw.line(
            surf,
            gold_color,
            (xp_bar_topleft_x, xp_bar_topleft_y),
            (xp_bar_topleft_x + xp_bar_length, xp_bar_topleft_y),
            2,
        )
        pygame.draw.line(
            surf,
            gold_color,
            (xp_bar_topleft_x, xp_bar_topleft_y + xp_bar_height),
            (xp_bar_topleft_x + xp_bar_length, xp_bar_topleft_y + xp_bar_height),
            2,
        )

    def pickup(self, item, time):
        item.activate(self, time)
        item.kill()

    def update(self, time, keys_pressed, mouse_pos, mouse_keys):

        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery
        self.current_time = time
        has_tp = False
        old_coordinates = [self.rect.centerx, self.rect.centery]
        # if (
        #     keys_pressed[pygame.K_o]
        #     and self.current_time - self.last_orbs_buff > self.orbs_buff_cooldown
        # ):
        #     self.create_rotating_orbs(8, 400, self.orbs_buff_duration, -1)
        #     self.create_rotating_orbs(8, 600, self.orbs_buff_duration)
        #     self.last_orbs_buff = time
        # # if keys_pressed[pygame.K_n]:
        # #     self.level_up()
        # # if keys_pressed[pygame.K_b]:
        # #     gamestate.spawn_boss(500)
        # if keys_pressed[pygame.K_LCTRL] and time - self.last_rewind > self.rewind_cooldown:
        #     old_self = pygame.sprite.Sprite(self.gamestate.camera_group)
        #     old_self.image = self.image
        #     old_self.rect = old_self.image.get_rect(center=self.rect.center)
        #     self.old_life = self.life
        #     self.old_velocity = self.velocity
        #     self.velocity = 2 * self.velocity
        #     self.rewind_image = old_self
        #     self.time_rewind = time + self.rewind_window
        #     self.last_rewind = time
        #     self.old_velocity = self.velocity
        #     self.velocity = 2 * self.velocity
        # if self.time_rewind:
        #     if time > self.time_rewind:
        #         self.rect.center = self.rewind_image.rect.center
        #         self.life = self.old_life
        #         self.velocity = self.old_velocity
        #         self.rewind_image.kill()
        #         self.time_rewind = False
        #         self.reset_orbs()
        #         has_tp = True
        if keys_pressed[pygame.K_SPACE] and time - self.last_tp > self.tp_cooldown:
            self.rect.x += self.direction_vector[0] * self.tp_distance
            self.rect.y += self.direction_vector[1] * self.tp_distance
            self.last_tp = time
            self.reset_orbs()
            tp_anim(self, self.gamestate)
            has_tp = True
            pygame.mixer.Sound.play(tp_sound)
        self.offset = self.gamestate.camera_group.offset
        self.direction = self.direction_vector[0]
        self.rect.x += self.direction_vector[0]
        self.rect.y += self.direction_vector[1]
        if self.direction > 0:
            self.image = self.non_flip_image
        elif self.direction < 0:
            self.image = self.flip_image

        self.direction_vector = [0, 0]
        self.attack(keys_pressed, mouse_pos, mouse_keys)
        new_coordinates = [self.rect.centerx, self.rect.centery]
        self.delta_position = (
            new_coordinates[0] - old_coordinates[0],
            new_coordinates[1] - old_coordinates[1],
        )
        if not has_tp:
            self.rotating_orbs.update()
        self.shuriken_ammo_refund()
        check_for_obstacles(self)

    def shuriken_ammo_refund(self):
        if (
            self.current_time - self.last_shuriken_ammo_refund > self.shuriken_ammo_cooldown
            and self.shuriken_ammo + len(self.gamestate.shurikens.sprites())
            < self.max_shuriken_ammo + 2
        ):  # max +2 flying shurikens at the same time
            self.shuriken_ammo += 1
            self.last_shuriken_ammo_refund = self.current_time

    def move(self, keys):
        vel = self.velocity / (np.sqrt(2))
        if keys[pygame.K_q] and keys[pygame.K_z]:
            self.direction_vector = np.array([-vel, -vel])
        elif keys[pygame.K_q] and keys[pygame.K_s]:
            self.direction_vector = np.array([-vel, vel])
        elif keys[pygame.K_d] and keys[pygame.K_z]:
            self.direction_vector = np.array([vel, -vel])
        elif keys[pygame.K_d] and keys[pygame.K_s]:
            self.direction_vector = np.array([vel, vel])
        elif keys[pygame.K_q]:
            self.direction_vector = np.array([-self.velocity, 0])
        elif keys[pygame.K_z]:
            self.direction_vector = np.array([0, -self.velocity])
        elif keys[pygame.K_s]:
            self.direction_vector = np.array([0, self.velocity])
        elif keys[pygame.K_d]:
            self.direction_vector = np.array([self.velocity, 0])
        else:
            self.direction_vector = np.zeros([2])


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
