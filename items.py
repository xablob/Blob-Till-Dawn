import numpy as np
import pygame

from game_init import camera_group
from music import xp_sound_1, xp_sound_2, xp_sound_3, xp_sound_4, xp_sound_5
from spritesheet import SpriteSheet
from utilities import reshape

xp_sounds = [xp_sound_1, xp_sound_2, xp_sound_3, xp_sound_4, xp_sound_5]
items_spritesheet = SpriteSheet("Assets/items.png")

# i = np.random.randint(0, 14)
# j = np.random.randint(0, 8)
i, j = 6, 5
# ring = items_spritesheet.image_at((i*50, j*50,50,50))
ring = items_spritesheet.image_at((30 + i * 60, 25 + j * 60, 60, 60))
ring.set_colorkey((0, 0, 0))
ring = reshape(ring, 2)
ring = ring.convert_alpha()


class Items(pygame.sprite.Group):
    def __init__(self):
        super().__init__()


items = Items()

# elixir_image = pygame.image.load("121.png").convert_alpha()
# elixir_image = pygame.image.load("PotionIcon (1).png")
elixir_image = pygame.image.load("Assets/pot of rose potion.png")
# elixir_image = pygame.transform.chop(elixir_image, (30,100,60,100))
# elixir_image.set_colorkey((0,0,0))
# elixir_image = elixir_image.convert_alpha()
elixir_image = reshape(elixir_image, 50)


item_images = {"Ring": ring, "Elixir": elixir_image, "XP_globe": elixir_image}


class Item(pygame.sprite.Sprite):
    def __init__(self, pos, item_name):
        super().__init__(camera_group, items)
        self.image = item_images[item_name]
        pos_randomisée = (
            (pos[0] + 5 * np.random.normal(0, 1)),
            (pos[1] + 5 * np.random.normal(0, 1)),
        )
        self.rect = self.image.get_rect(topleft=pos_randomisée)
        self.date_of_birth = pygame.time.get_ticks()
        self.max_duration = 10000

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def update(self, hero, time):
        """Regarder si le héros est au dessus de l'objet"""
        if self.is_colliding_with(hero):
            hero.pickup(self, time)
        current_time = pygame.time.get_ticks()
        if current_time - self.date_of_birth > self.max_duration:
            self.kill()


class Ring(Item):
    def __init__(self, pos, item_name, source):
        super().__init__(pos, item_name)
        self.item_type = "Ring"

    def activate(self, entity, time):
        pass


class XP_globe(Item):
    def __init__(self, pos, item_name, source):
        super().__init__(pos, item_name)
        self.xp_value = source.xp_on_death
        self.item_type = "XP_Globe"

    def activate(self, entity, time):
        entity.add_xp(self.xp_value)
        xp_sound = xp_sounds[2]
        xp_sound.play()


class Elixir(Item):
    def __init__(self, pos, item_name, source):
        super().__init__(pos, item_name)
        self.item_type = "Elixir"

    def activate(self, entity, time):
        entity.forever_lost_life += 0.1 * entity.max_life
        entity.life = entity.max_life - entity.forever_lost_life


item_classes = {"Ring": Ring, "XP_globe": XP_globe, "Elixir": Elixir}
