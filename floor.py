import numpy as np
import pygame

from params import dimx, dimy, end_map_x, end_map_y, start_map_x, start_map_y
from spritesheet import lava_spritesheet
from target_tag import TagList, TargetTag
from utilities import harmonize, reshape

lava_tiles = [
    lava_spritesheet.image_at((0, 0, 128, 64)),
    lava_spritesheet.image_at((128, 0, 128, 64)),
    lava_spritesheet.image_at((0, 64, 128, 64)),
    lava_spritesheet.image_at((128, 64, 128, 64)),
]

old_rock_tile = pygame.image.load("Assets/floor-tiles.png").convert_alpha()  # unused

coeff_reshape = 2

stone_tile = reshape(pygame.image.load("Assets/isometric/stone.png").convert_alpha(), coeff_reshape)
snow_tile = reshape(pygame.image.load("Assets/isometric/snow.png").convert_alpha(), coeff_reshape)
dirt_tile = reshape(pygame.image.load("Assets/isometric/dirt.png").convert_alpha(), coeff_reshape)
plant_tile = reshape(pygame.image.load("Assets/isometric/plant.png").convert_alpha(), coeff_reshape)
jungle_tile = reshape(
    pygame.image.load("Assets/isometric/jungle.png").convert_alpha(), coeff_reshape
)
sand_tile = reshape(pygame.image.load("Assets/isometric/sand.png").convert_alpha(), coeff_reshape)
brick_tile = reshape(pygame.image.load("Assets/isometric/brick.png").convert_alpha(), coeff_reshape)
concrete_tile = reshape(
    pygame.image.load("Assets/isometric/concrete.png").convert_alpha(), coeff_reshape
)
cretebrick_tile = reshape(
    pygame.image.load("Assets/isometric/cretebrick.png").convert_alpha(), coeff_reshape
)
rock_tile = reshape(pygame.image.load("Assets/isometric/rock.png").convert_alpha(), coeff_reshape)
water_tile = reshape(pygame.image.load("Assets/Water_tiles/water_v01.png"), coeff_reshape)

dim_tile = stone_tile.get_size()
dim_tile = lava_tiles[0].get_size()
TILE_SIZE = stone_tile.get_size()[0]


n_tiles_x = int((end_map_x - start_map_x) // dim_tile[0])
n_tiles_y = int((end_map_y - start_map_y) // dim_tile[1])


tiles = {
    "water": water_tile,
    "stone": stone_tile,
    "dirt": dirt_tile,
    "plant": plant_tile,
    "jungle": jungle_tile,
    "sand": sand_tile,
    "snow": snow_tile,
    "brick": brick_tile,
    "concrete": concrete_tile,
    "cretebrick": cretebrick_tile,
    "rock": rock_tile,
}

name_ids = [
    "water",
    "plant",
    "jungle",
    "plant",
    "jungle",
    "sand",
    "jungle",
    "jungle",
    "plant",
    "plant",
    "jungle",
]

n_possible_tiles = len(tiles)

map_floors_id = np.random.randint(0, 6, [n_tiles_x, n_tiles_y])
map_floors_id = np.zeros([n_tiles_x, n_tiles_y])

harmonize(map_floors_id)


class Floor(pygame.sprite.Sprite):
    def __init__(self, gamestate, pos, i, j, name_id=False):
        super().__init__(gamestate.ground)
        if name_id == False:
            index = np.random.randint(1, len(tiles.keys()))
            name = name_ids[index]
        elif name_id == "water":
            name = "water"
        else:
            name = name_ids[name_id]
        # print(name)
        self.i = i
        self.j = j
        self.image = tiles[name]
        self.original_image = self.image
        # i = np.random.randint(0, 4)
        # self.image = lava_tiles[i]
        self.name = name
        self.rect = self.image.get_rect(topleft=pos)
        self.show = True
        self.is_activated = False
        self.tag_list = TagList()
        self.base_damage = 5
        self.current_time = pygame.time.get_ticks()
        self.gamestate = gamestate

    def activate_lava(self):
        self.activated = True
        i = np.random.randint(0, 4)
        self.image = lava_tiles[i]

    def disactivate_lava(self):
        self.activated = False
        self.image = self.original_image

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def update(self, hero_center_x, hero_center_y, time):
        self.current_time = time
        x, y = self.rect.x, self.rect.y
        if abs(x - hero_center_x) > 0.8 * dimx or abs(y - hero_center_y) > 0.8 * dimy:
            self.show = False
        else:
            self.show = True
            if self.is_activated:
                entity = self.gamestate.hero
                if self.is_colliding_with(entity) and self.tag_list.does_not_contain(entity):
                    entity.life -= self.base_damage
                    if entity.life <= 0:
                        entity.part_vers_une_destination_mystérieuse()
                        # self.source.kills += 1
                    else:
                        TargetTag(self.current_time, self, entity, 250)


def initiate_floor(gamestate):
    len_x = dim_tile[0] * n_tiles_x
    len_y = dim_tile[1] * n_tiles_y
    start_draw_x = -len_x // 2
    start_draw_y = -len_y // 2
    offset_x = dim_tile[0] // 2
    offset_y = dim_tile[1] // 2
    for i in range(n_tiles_x):
        for j in range(n_tiles_y):
            Floor(
                gamestate,
                (
                    start_draw_x + i * dim_tile[0] + offset_x,
                    start_draw_y + j * dim_tile[1] + offset_y,
                ),
                i,
                j,
                map_floors_id[i][j],
            )
            Floor(
                gamestate,
                (start_draw_x + i * dim_tile[0], start_draw_y + j * dim_tile[1]),
                i,
                j,
                map_floors_id[i][j],
            )
