import pygame


class TagList(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def does_not_contain(self, entity):
        for tag in self.sprites():
            if tag.target.id == entity.id:
                return False
        return True


class TargetTag(pygame.sprite.Sprite):
    def __init__(self, time, source, entity, duration=200):
        super().__init__(source.tag_list)
        self.duration = duration
        self.target = entity
        self.birthdate = time

    def update(self, time):
        if time - self.birthdate > self.duration:
            self.kill()
