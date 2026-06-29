import numpy as np
import pygame

from aoe_effects import Rectangular_beam
from items import item_classes
from music import alert_sound, rock_sound
from obstacles import EnemyObstacle
from projectile import ProjectileSkill, arcane_orb_image
from utilities import Event_on_health_threshold, get_angle, reshape

coeff_petit = 2

fire_image_length = 50


class Boss(pygame.sprite.Sprite):
    def __init__(self, gamestate, camera_group):
        alert_sound.play()
        super().__init__(camera_group, gamestate.boss_group)
        self.image = reshape(
            pygame.image.load("Assets/FluffyBlob/CharFluffyYellow.png").convert_alpha(), 2
        )
        self.rect = self.image.get_rect()
        self.rect.x = gamestate.hero.rect.x + 500
        self.rect.y = gamestate.hero.rect.y + 0
        self.gamestate = gamestate
        self.dimx = gamestate.dimx
        self.offset = pygame.math.Vector2(0, 0)
        self.camera_group = camera_group
        self.life = 5000
        self.max_life = self.life
        self.non_flip_image = self.image
        self.flip_image = pygame.transform.flip(self.image, True, False)
        self.potential_targets = gamestate.hero_group
        self.target = gamestate.hero
        self.velocity = 0.5
        self.base_velocity = self.velocity
        self.id = "Boss"
        self.blobtype = "???"
        self.number_of_splits = 0
        self.status = "Agressive"
        self.auto_skills = {
            "Fireball": ProjectileSkill(gamestate, "Fireball", "Skillshot", arcane_orb_image)
        }
        self.cooldowns = {}
        self.initial_cooldowns = {}
        self.date_of_last_attack = {}
        for skill in self.auto_skills.values():
            self.cooldowns[skill.name] = skill.cooldown
            self.initial_cooldowns[skill.name] = skill.cooldown
            self.date_of_last_attack[skill.name] = -9999
        self.angle_range = "All directions"
        self.number_of_proj = 0
        self.sequential_number_of_proj = 0
        self.number_of_chains = 0
        self.projectile_speed = 17
        self.projectile_duration = 5
        self.attack_power = 4
        self.xp_on_death = 10
        self.offset_radius = self.rect.width / 2
        self.kills = 0
        self.make_it_rain_cooldown = 3000
        self.current_time = pygame.time.get_ticks()
        self.last_rain = -99999999999
        self.can_make_it_rain = True
        self.rain_mode = "Lines"
        self.n_fires = 15
        self.fire_length = self.n_fires * fire_image_length
        self.has_started_raining = False
        self.rain_counts = -1
        self.drop_table = {"Elixir": 100}
        self.has_reached_midlife = False
        self.bool_draw_health = True
        self.is_obstacle = False

        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery

        self.coeff_object_damage = 0.5

        self.events = pygame.sprite.Group()
        Event_on_health_threshold(self, 0.5, emprisonne_le_joueur)
        Event_on_health_threshold(self, 0.8, first_beams)

    def on_death_effect(self):
        pass

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def make_it_rain(self):
        self.rain_counts += 0
        for floor in self.gamestate.ground.sprites():
            if (floor.i + floor.j + self.rain_counts) % 4 == 0:
                floor.activate_lava()
            else:
                floor.disactivate_lava()

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
                (self.dimx / 2 - health_rect.size[0] / 2, 20),
                health_rect.size,
                (0, 0, 0),
                (255, 0, 0),
                (0, 255, 0),
                self.life / self.max_life,
            )

    def part_vers_une_destination_mystérieuse(self, source):
        self.on_death_effect()
        self.drop_items()
        self.kill()

    def drop_items(self):
        weights = [value for value in self.drop_table.values()]
        total_weight = np.random.uniform(0, sum(weights))
        partial_sum = 0
        i = -1
        while partial_sum <= total_weight:
            i += 1
            partial_sum += np.array(weights)[i]
        item_name = [key for key in self.drop_table.keys()][i]
        item_classes[item_name](self.rect.topleft, item_name, self)

    def update(self, time):
        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery

        self.offset = self.camera_group.offset
        self.current_time = time
        self.life_ratio = self.life / self.max_life
        self.velocity = ((2 - self.life_ratio) ** 2) * self.base_velocity
        self.number_of_proj = number_of_proj(self.life_ratio)
        if self.life_ratio < 0.8 and self.life_ratio >= 0.6:
            self.sequential_number_of_proj = 1
        elif self.life_ratio < 0.6 and self.life_ratio >= 0.3:
            self.sequential_number_of_proj = 2
        elif self.life_ratio < 0.3:
            self.sequential_number_of_proj = 3
            self.cooldowns["Fireball"] = self.initial_cooldowns["Fireball"] / 1.5

        self.events.update()

        # if not self.has_reached_midlife:
        #     if self.life_ratio < 0.5:
        #         self.has_reached_midlife = True
        #         self.emprisonne_le_joueur()

        # if self.can_make_it_rain:
        #     if self.current_time - self.last_rain > self.make_it_rain_cooldown:
        #         self.make_it_rain()
        #         self.last_rain = self.current_time
        # Find a new direction
        self.direction_vector = np.array(
            [
                self.target.rect.centerx - self.rect.centerx,
                self.target.rect.centery - self.rect.centery,
            ]
        )
        if np.linalg.norm(self.direction_vector) != 0:
            self.direction_vector = (
                self.direction_vector / np.linalg.norm(self.direction_vector) * self.velocity
            )
        if self.status == "Agressive":
            for skill in self.auto_skills.values():
                if (
                    self.current_time - self.date_of_last_attack[skill.name]
                    > self.cooldowns[skill.name]
                ):
                    skill.activate(self.target, self)
                    self.date_of_last_attack[skill.name] = self.current_time
        # Once direction has been found, the entity moves and we update its image if necessary
        self.direction = self.direction_vector[0]
        self.rect.x += self.direction_vector[0]
        self.rect.y += self.direction_vector[1]
        if self.direction >= 0:
            self.image = self.non_flip_image
        else:
            self.image = self.flip_image


def number_of_proj(life_ratio):
    return 1 + int(10 * (1 - life_ratio))


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


def emprisonne_le_joueur(caster):
    rock_sound.play()
    radius = 130

    player_x, player_y = caster.gamestate.hero.rect.centerx, caster.gamestate.hero.rect.centery

    vector = np.array([player_x - caster.rect.centerx, player_y - caster.rect.centery])
    vector = radius * vector / np.linalg.norm(vector)

    alpha = get_angle(vector)
    alpha_max = alpha + np.pi / 2
    alpha_min = alpha - np.pi / 2
    alpha_1 = alpha + np.pi / 4
    alpha_2 = alpha - np.pi / 4

    EnemyObstacle(
        player_x + 1.1 * radius * np.cos(alpha), player_y + 1.1 * radius * np.sin(alpha), 2
    )
    EnemyObstacle(player_x + radius * np.cos(alpha_max), player_y + radius * np.sin(alpha_max), 2)
    EnemyObstacle(player_x + radius * np.cos(alpha_min), player_y + radius * np.sin(alpha_min), 2)
    EnemyObstacle(player_x + radius * np.cos(alpha_1), player_y + radius * np.sin(alpha_1), 2)
    EnemyObstacle(player_x + radius * np.cos(alpha_2), player_y + radius * np.sin(alpha_2), 2)


from music import alert_sound, rock_sound
from obstacles import EnemyObstacle


def first_beams(entity):
    Rectangular_beam(entity.gamestate,
        10000,
        50,
        entity,
        np.random.uniform(0, 2 * np.pi),
        entity.rect.centerx,
        entity.rect.centery,
        1 * np.pi / 180,
    )
    Rectangular_beam(entity.gamestate,
        10000,
        50,
        entity,
        np.random.uniform(0, 2 * np.pi),
        entity.rect.centerx,
        entity.rect.centery,
        2 * np.pi / 180,
    )
    Rectangular_beam(entity.gamestate,
        10000,
        50,
        entity,
        np.random.uniform(0, 2 * np.pi),
        entity.rect.centerx,
        entity.rect.centery,
        3*np.pi / 180,
    )
