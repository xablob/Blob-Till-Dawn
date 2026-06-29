import numpy as np
import pygame

from game_init import camera_group, gamestate
from gamestate import dimx, dimy
from items import item_classes
from map_objects import on_death_anim
from utilities import reshape, reshape_until

mob_size = 80
size_dispersion = 30
min_size = 60

can_merge = False

pixels = 1080 // 3

on_death_animation = False

coeff_petit = 5 * np.sqrt(2)
blobtypes_names = [
    "Sombregouffre",
    "Épouvantâcre",
    "Maléfion",
    "Nécrognome",
    "Vilombrage",
    "Démonfou",
    "Horriflamme",
    "Pestigoule",
    "Faucheveine",
    "Terrobscur",
    "Ombrénigme",
    "Fulgurnoir",
    "Sinistrelle",
    "Vampitrouille",
    "Charnonuit",
    "Abysseflamme",
    "Squelettex",
    "Miasmarak",
    "Spectragore",
    "Flammorgue",
    "Maladragon",
    "Ombremonde",
    "Frissensombre",
    "Putrigoule",
    "Lavevenin",
]


class Enemy(pygame.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, spawn_date):
        # Call the parent class (Sprite) constructor
        super().__init__(camera_group, gamestate.enemies_group)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        p = np.random.randint(1, 3)

        self.dispersion = np.random.normal(0, size_dispersion)
        if mob_size + self.dispersion > min_size:
            self.size = [mob_size + self.dispersion, mob_size + self.dispersion]
        else:
            self.size = [min_size, min_size]
        self.id = "Mob_" + str(gamestate.mob_id)
        gamestate.mob_id += 1
        if p == 0:
            self.non_flip_image = reshape(
                pygame.image.load("Assets/FluffyBlob/CharFluffyYellow.png").convert_alpha(),
                coeff_petit,
            )
            self.flip_image = reshape(
                pygame.transform.flip(
                    pygame.image.load("Assets/FluffyBlob/CharFluffyYellow.png").convert_alpha(),
                    True,
                    False,
                ),
                coeff_petit,
            )
        elif p == 1:
            self.non_flip_image = reshape(
                pygame.image.load("Assets/FluffyBlob/CharFluffyGreen.png").convert_alpha(),
                coeff_petit,
            )
            self.flip_image = reshape(
                pygame.transform.flip(
                    pygame.image.load("Assets/FluffyBlob/CharFluffyGreen.png").convert_alpha(),
                    True,
                    False,
                ),
                coeff_petit,
            )
        else:
            self.non_flip_image = reshape(
                pygame.image.load("Assets/FluffyBlob/CharFluffy.png").convert_alpha(),
                coeff_petit,
            )
            self.flip_image = reshape(
                pygame.transform.flip(
                    pygame.image.load("Assets/FluffyBlob/CharFluffy.png").convert_alpha(),
                    True,
                    False,
                ),
                coeff_petit,
            )

        self.image = self.flip_image
        self.image = reshape_until(self.image, self.size)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.x = np.random.uniform(0, dimx)
        self.rect.y = np.random.uniform(0, dimy)
        self.flip = False
        self.direction = 1
        self.blobtype = blobtypes_names[np.random.randint(0, len(blobtypes_names))]
        self.velocity = gamestate.enemy_baseline_velocity * (1 - self.dispersion / 100)
        self.velocity = max(1.2, self.velocity)
        self.base_velocity = self.velocity
        self.direction_vector = np.zeros([2])
        self.status = gamestate.baseline_status
        self.life = gamestate.mob_baselife + self.dispersion
        # print(self.life)
        self.offset = pygame.math.Vector2(0, 0)
        self.has_found_target = False
        self.xp_on_death = 1 * max(1, self.life / gamestate.mob_baselife) ** 1.5
        self.max_life = self.life
        self.skills = ["bonk"]
        self.cooldown = 2000
        self.date_of_last_attack = -9999
        self.date = spawn_date
        self.spawn_date = self.date
        self.base_damage = 2
        self.start_of_attack = self.spawn_date + 500
        self.temps_parcours_moyen = 300
        self.date_of_last_direction_switch = -99999
        self.potential_targets = gamestate.hero_group
        self.select_random_target()
        self.type = "entity"

        self.final_position = (0, 0)
        self.drop_table = {"Ring": 0, "XP_globe": 95}

        self.is_obstacle = False
        self.bool_draw_health = True

        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

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

        # if i == 0:
        #     item = Item(self.rect.topleft, "ring")
        #     item.rect.center = self.rect.center

    def print(self):
        print("Hi my rect is at ", self.rect.x, self.rect.y)

    def on_death_effect(self):

        if on_death_animation:
            on_death_anim(self)
        death_sound = pygame.mixer.Sound("Assets/on_death_effects/bubble_01.ogg")
        death_sound.set_volume(0)
        pygame.mixer.Sound.play(death_sound)

    def coordinates(self):
        return [self.rect.centerx, self.rect.centery]

    def distance(self, sprite):
        return (
            (self.rect.centerx - sprite.rect.centerx) ** 2
            + (self.rect.centery - sprite.rect.centery) ** 2
        ) ** 0.5

    def generate_random_direction_vector(self):
        angle = np.random.uniform(0, 2 * np.pi)
        new_x = 100 * np.cos(angle)
        new_y = 100 * np.sin(angle)
        return np.array([new_x, new_y])

    def has_line_of_sight(self, entity):
        return True

    def update(self, time):
        self.last_x = self.rect.centerx
        self.last_y = self.rect.centery

        self.offset = camera_group.offset
        self.date = time
        if self.date > self.start_of_attack and not self.has_found_target:
            self.status = "Agressive"
            self.select_random_target()
            self.has_found_target = True

        # Find a new direction
        if self.status == "Agressive":
            if self.has_line_of_sight(self.target):
                self.direction_vector = np.array(
                    [
                        self.target.rect.centerx - self.rect.centerx,
                        self.target.rect.centery - self.rect.centery,
                    ]
                )
            else:
                "despair"
        else:
            if self.status == "Passive":
                if self.date - self.date_of_last_direction_switch > self.temps_parcours_moyen:
                    self.direction_vector = self.generate_random_direction_vector()
                    self.date_of_last_direction_switch = self.date
            if self.status == "Go to position":
                self.direction_vector = np.array(
                    [
                        self.final_position[0] - self.rect.centerx,
                        self.final_position[1] - self.rect.centery,
                    ]
                )
                if (
                    abs(self.final_position[0] - self.rect.centerx) < 10
                    and abs(self.final_position[1] - self.rect.centery) < 10
                ):
                    self.velocity = 0

        if np.linalg.norm(self.direction_vector) != 0:
            self.direction_vector = (
                self.direction_vector / np.linalg.norm(self.direction_vector) * self.velocity
            )

        # Once direction has been found, the entity moves and we update its image if necessary
        self.direction = self.direction_vector[0]
        self.rect.x += self.direction_vector[0]
        self.rect.y += self.direction_vector[1]
        if self.direction >= 0:
            self.image = self.non_flip_image
        else:
            self.image = self.flip_image
        self.image = reshape_until(self.image, self.size)

        # Attack
        if self.status == "Agressive":
            if self.date - self.date_of_last_attack > self.cooldown:
                for entity in self.potential_targets:
                    if self.is_colliding_with(entity):
                        entity.life -= self.base_damage
                        self.date_of_last_attack = self.date
                        if entity.life <= 0:
                            entity.part_vers_une_destination_mystérieuse(self)
                            # for orb in entity.rotating_orbs.sprites():
                            #     orb.kill()
                            # gamestate.last_hero_coordinates = entity.rect.center
                            # #print(gamestate.last_hero_coordinates)
                            # gamestate.form_the_l()
                            # entity.kill()
                            # self.select_random_target()
        #print("Temps réel / date de spawn / temps gamestate / temps abs gamestate : ", self.date, self.spawn_date, gamestate.time, gamestate.absolute_time)
        self.velocity = max(1, ((self.date - self.spawn_date) / 2000) ** 0.5) * self.base_velocity
        
        

    def select_random_target(self):
        n_targets = len(self.potential_targets.sprites())
        if n_targets > 0:
            index_target = np.random.randint(0, n_targets)
            self.target = self.potential_targets.sprites()[index_target]
        else:
            self.status = "Passive"

    def is_alive(self):
        return self.life > 0

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
