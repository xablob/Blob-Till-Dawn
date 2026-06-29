import numpy as np
import pygame

from params import end_map_x, end_map_y, start_map_x, start_map_y
from spritesheet import on_death_explo
from target_tag import TagList, TargetTag
from utilities import reshape, reshape_until

map_objects = pygame.sprite.Group()
dimx = 1920
dimy = 1080

coords_id_table = {}
coords_id_table["On-death explosion"] = []
coords_id_table["explosion"] = []
for j in range(4):
    for i in range(8):
        coords_id_table["On-death explosion"].append((0 + i * 256, 0 + j * 256, 256, 256))

for j in range(4):
    for i in range(8):
        coords_id_table["explosion"].append((0 + i * 256, 0 + j * 256, 256, 256))
animation_table = {}

animation_table["On-death explosion"] = on_death_explo

on_death_explo_images = []

burning_fire_images = []


def on_death_anim(entity, gamestate):
    SpritesheetAnimation(gamestate, 
        "On-death explosion", [entity.rect.centerx, entity.rect.centery], entity, 150
    )


def tp_anim(entity, gamestate):
    on_death_anim(entity, gamestate)
    # explosion_anim(entity)


def explosion_anim(entity):
    SpritesheetAnimation("explosion", [entity.rect.centerx, entity.rect.centery], entity, 200)


for i in range(1, 40):
    name = "Assets/fire_1_40/fire_1f_40_" + str(i) + ".png"
    image = pygame.image.load(name).convert_alpha()
    image = pygame.transform.chop(image, (0, 0, 0, 42))
    # image = pygame.transform.chop(image, (0, 0, 20, 20))
    burning_fire_images.append(image)
animation_table["Burning Fire"] = burning_fire_images

trees = []
for i in range(1, 9):
    name = "Assets/tree/Sprite_0" + str(i) + ".png"
    image = reshape(pygame.image.load(name).convert_alpha(), 4)
    name_table = "Tree " + str(i)
    animation_table[name_table] = [image]


class Tree(pygame.sprite.Sprite):
    def __init__(self, gamestate, x, y):
        super().__init__(gamestate.camera_group.map_objects)
        name = "Assets/tree/Sprite_0" + str(np.random.randint(1, 6)) + ".png"
        self.image = reshape(pygame.image.load(name).convert_alpha(), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.offset = pygame.math.Vector2(0, 0)


def create_trees(gamestate, n_trees=5):
    for _ in range(n_trees):
        x = np.random.uniform(start_map_x, end_map_x)
        y = np.random.uniform(start_map_y, end_map_y)
        Tree(gamestate, x, y)


def create_fire(gamestate, coordinates, size=1):
    Animation(gamestate, "Burning Fire", coordinates, size)


def create_fires(gamestate, n_fires=5):
    for _ in range(n_fires):
        x = np.random.uniform(start_map_x, end_map_x)
        y = np.random.uniform(start_map_y, end_map_y)
        create_fire(gamestate, [x, y])


def create_animated_fires(gamestate, n_fires=5):
    for _ in range(n_fires):
        x = np.random.uniform(start_map_x, end_map_x)
        y = np.random.uniform(start_map_y, end_map_y)
        fire = AnimatedFire(gamestate, (x, y), False)
        fire.expire = False


class Animation(pygame.sprite.Sprite):
    def __init__(self, gamestate, name, coordinates, size):
        # Call the parent class (Sprite) constructor
        super().__init__(gamestate.camera_group.map_objects)

        self.name = name

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.images = [reshape(image, size) for image in animation_table[self.name]]
        self.image_index = 0
        self.image = self.images[self.image_index]
        map_objects.add(self)

        self.image_duration = 10
        self.date = pygame.time.get_ticks()
        self.last_switch = self.date

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.centerx = coordinates[0]
        self.rect.centery = coordinates[1]
        print("Widht : ", self.rect.width, " Height : ", self.rect.height)

    def update(self):
        self.date = pygame.time.get_ticks()
        if self.date - self.last_switch > self.image_duration:
            self.image_index += 1
            if self.image_index > len(self.images) - 1:
                self.image_index = 0
            self.image = self.images[self.image_index]
            self.last_switch = self.date


class AnimatedFire(pygame.sprite.Sprite):
    def __init__(self, gamestate, coordinates, source=False):
        # Call the parent class (Sprite) constructor
        super().__init__(gamestate.camera_group.map_objects)
        self.offset = pygame.math.Vector2(0, 0)
        self.name = "Burning Fire"
        self.expire = True
        self.gamestate = gamestate

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.images = [image for image in animation_table[self.name]]
        self.image_index = 0
        self.image = self.images[self.image_index]
        map_objects.add(self)
        self.source = source
        if self.source:
            self.potential_targets = self.source.potential_targets
        else:
            self.potential_targets = gamestate.hero_group
        self.image_duration = 5
        self.base_damage = 0
        self.duration = 2500
        self.current_time = pygame.time.get_ticks()
        self.spawn_time = self.current_time
        self.last_switch = self.current_time
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.centerx = coordinates[0]
        self.rect.centery = coordinates[1]
        self.tag_list = TagList()

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def update(self):
        self.offset = self.gamestate.camera_group.offset
        # draw_rect(self, camera_group.win)
        self.current_time = pygame.time.get_ticks()
        self.tag_list.update(self.current_time)
        if self.expire:
            if self.current_time - self.spawn_time > self.duration:
                self.kill()
        if self.current_time - self.last_switch > self.image_duration:
            self.image_index += 1
            if self.image_index > len(self.images) - 1:
                self.image_index = 0
            self.image = self.images[self.image_index]
            self.last_switch = self.current_time

        for entity in self.potential_targets.sprites():
            if self.is_colliding_with(entity) and self.tag_list.does_not_contain(entity):
                entity.life -= self.base_damage
                if entity.life <= 0:
                    entity.part_vers_une_destination_mystérieuse()
                else:
                    TargetTag(self.current_time, self, entity, 250)


class SpritesheetAnimation(pygame.sprite.Sprite):
    def __init__(self, gamestate, name, coordinates, source, size):
        # Call the parent class (Sprite) constructor
        super().__init__(gamestate.camera_group)

        self.name = name
        self.source = source

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.spritesheet = animation_table[self.name]
        self.coord_ids = coords_id_table[self.name]

        self.image_index = 0
        self.image_coord = self.coord_ids[self.image_index]
        self.image = self.spritesheet.image_at(self.image_coord)
        # print(self.image_coord)
        self.image.set_colorkey((0, 0, 0))
        self.image = self.image.convert_alpha()
        self.source_size = [size, size]

        self.image = reshape_until(self.image, self.source_size)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 0
        map_objects.add(self)

        self.image_duration = 5
        self.loop_duration = 275
        self.date = pygame.time.get_ticks()
        self.last_switch = self.date
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.centerx = coordinates[0]
        self.rect.centery = coordinates[1]

    def update(self):
        self.date = pygame.time.get_ticks()
        self.lifetime = self.date - self.spawn_time
        self.image_index = min(
            int(len(self.coord_ids) * self.lifetime / self.loop_duration),
            len(self.coord_ids) - 1,
        )
        if self.image_index >= len(self.coord_ids) - 1:
            self.image_index -= 1
            self.kill()
        self.image_coord = self.coord_ids[self.image_index]
        self.image = self.spritesheet.image_at(self.image_coord)
        self.image = reshape_until(self.image, self.source_size)
