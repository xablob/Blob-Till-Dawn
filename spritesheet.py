import pygame


class SpriteSheet:
    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
            self.sheet.set_colorkey((20, 20, 20))
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        image.set_colorkey((0, 0, 0))
        image = image.convert_alpha()
        image.set_colorkey((0, 0, 0))
        image = image.convert_alpha()
        # if colorkey is not None:
        #     if colorkey is -1:
        #         colorkey = image.get_at((0,0))
        #     image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect) for rect in rects]

    def load_strip(self, rect, image_count):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3]) for x in range(image_count)]
        return self.images_at(tups)


# def init_spritesheets():
#     global on_death_explo
#     global tiles_spritesheet
#     global lava_spritesheet
#     global lightning_spritesheet
#     on_death_explo = SpriteSheet("Assets/on_death_effects/explosionFull.png")
#     tiles_spritesheet = SpriteSheet("Assets/tiles_spritesheet/full_tiles.png")
#     lava_spritesheet = SpriteSheet("Assets/lava.png")
#     lightning_spritesheet = SpriteSheet("Assets/lightning_spritesheet/impact07.png")

on_death_explo = SpriteSheet("Assets/on_death_effects/explosionFull.png")
tiles_spritesheet = SpriteSheet("Assets/tiles_spritesheet/full_tiles.png")
lava_spritesheet = SpriteSheet("Assets/lava.png")
lightning_spritesheet = SpriteSheet("Assets/lightning_spritesheet/impact07.png")
