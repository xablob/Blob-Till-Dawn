import numpy as np
import pygame

from game_init import camera_group, gamestate
from projectile import water_orb_image
from spritesheet import SpriteSheet
from utilities import reshape

portal_spritesheet = SpriteSheet("Assets/teleport_512.png")
portal_image = portal_spritesheet.image_at((0, 256, 512, 256))
portal_image.set_colorkey((0, 0, 0))
portal_image = portal_image.convert_alpha()
portal_image = reshape(portal_image, 5)

offset_dispersion = 80


colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "BLUE": (0, 0, 255),
    "RED": (255, 0, 0),
}
portals = gamestate.portals


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos, colorname=False):
        super().__init__(camera_group, portals)
        self.image = pygame.Surface((50, 50))
        self.image = portal_image
        self.is_hovered = False
        self.source = gamestate.hero
        if colorname:
            self.color = colors[colorname]
            self.name = colorname
        else:
            self.name = str(np.random.randint(0, 1000))
            self.color = np.random.randint(0, 255, 3)
        # self.image.fill(self.color)
        self.rect = self.image.get_rect(center=pos)
        self.spawn_date = pygame.time.get_ticks()
        self.current_time = self.spawn_date

    def show_redirection(self):
        portals_to_exclude = []
        final_portal = self
        for index_portal in range(len(gamestate.portals.sprites()) - 1):
            portals_to_exclude.append(final_portal)
            final_portal.draw_redirection(portals_to_exclude)
            final_portal = final_portal.find_nearest_portal(portals_to_exclude)

    def distance(self, sprite):
        return (
            (self.rect.centerx - sprite.rect.centerx) ** 2
            + (self.rect.centery - sprite.rect.centery) ** 2
        ) ** 0.5

    def find_nearest_portal(self, portals_to_exclude):
        min_distance = 999999999999999
        nearest_portal = False
        for portal in portals.sprites():
            if not portal.is_in([self] + portals_to_exclude):
                if self.distance(portal) < min_distance:
                    min_distance = self.distance(portal)
                    nearest_portal = portal
        return nearest_portal

    def is_in(self, portals_list):
        result = False
        for portal in portals_list:
            if portal.rect.x == self.rect.x and portal.rect.y == self.rect.y:
                result = True
        return result

    def update(self, skillshots, mouse_pos, time):
        for projectile in skillshots:
            if not projectile.has_taken_a_portal:
                if self.is_colliding_with(projectile):
                    self.translate(projectile)
        player = gamestate.hero
        if (
            self.is_colliding_with(player)
            and time - player.last_portal_tp > player.portal_tp_cooldown
        ):
            self.translate_player(player, time)

    def draw_redirection(self, portals_to_exclude):
        next_portal = self.find_nearest_portal(portals_to_exclude)
        if next_portal:
            pygame.draw.line(
                camera_group.win,
                self.color,
                self.rect.center + camera_group.offset,
                next_portal.rect.center + camera_group.offset,
                5,
            )

    def translate(self, projectile):
        portals_to_exclude = []
        final_portal = self
        for index_portal in range(len(portals) - 1):
            portals_to_exclude.append(final_portal)
            final_portal = final_portal.find_nearest_portal(portals_to_exclude)
            # print("len = ", len(portals_to_exclude))
        if not final_portal.is_in([self]):
            projectile.projectile_speed = 2.2 * projectile.projectile_speed
            projectile.rect.centerx, projectile.rect.centery = (
                final_portal.rect.centerx,
                final_portal.rect.centery,
            )
            projectile.has_taken_a_portal = True
            if projectile.source.id != self.source.id:
                projectile.source = self.source
                projectile.has_split = True
            projectile.potential_targets = self.source.potential_targets
            projectile.image = water_orb_image
            projectile.pierce = True
            # for index_copy in range(len(portals.sprites())):
            #     angle = projectile.angle + np.pi*((-1)**np.random.randint(0, 2))/2
            #     dispersion = np.random.uniform(0, offset_dispersion)
            #     offset = (dispersion*np.cos(angle), dispersion*np.sin(angle))
            #     projectile.copy(offset)
            angle = projectile.angle + np.pi / 2
            dispersion = np.random.uniform(0, offset_dispersion)
            offset = (dispersion * np.cos(angle), dispersion * np.sin(angle))
            projectile.copy(offset)
            angle = projectile.angle - np.pi / 2
            dispersion = np.random.uniform(0, offset_dispersion)
            offset = (dispersion * np.cos(angle), dispersion * np.sin(angle))
            projectile.copy(offset)

    def translate_player(self, player, time):

        portals_to_exclude = []
        final_portal = self
        for index_portal in range(len(portals) - 1):
            portals_to_exclude.append(final_portal)
            final_portal = final_portal.find_nearest_portal(portals_to_exclude)
            # print("len = ", len(portals_to_exclude))
        if not final_portal.is_in([self]):
            player.rect.centerx, player.rect.centery = (
                final_portal.rect.centerx,
                final_portal.rect.centery,
            )
            player.last_portal_tp = time
            gamestate.buff_enemies = True
            variation = [
                final_portal.rect.x - self.rect.x,
                final_portal.rect.y - self.rect.y,
            ]
            player.reset_orbs()

        # print(" ")
        # final_portal = portals.sprites()[np.random.randint(0, len(portals))]
        # projectile.rect.centerx, projectile.rect.centery = final_portal.rect.centerx, final_portal.rect.centery
        # projectile.has_taken_a_portal = True

    def is_colliding_with(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
# Portal((200, 0), "BLACK")
# Portal((400, 0), "WHITE")
# Portal((600, 0), "BLUE")
# Portal((-200,0), "RED")
