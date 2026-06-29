import json

import numpy as np
import pygame
import requests

from fonts import (
    big_font,
    delta_y,
    display_text,
    huge_font,
    margin_x,
    margin_y,
    normal_font,
    small_font,
)
from inputbox import TextInputBox
from params import dimx, dimy, draw_hitboxes, end_map_x, end_map_y, start_map_x, start_map_y
from utilities import generate_random_color


class CameraGroup(pygame.sprite.Group):
    def __init__(self, gamestate):
        super().__init__()
        self.name_input_box = TextInputBox(gamestate, dimx / 3, dimy / 2, 500, small_font)
        self.name_input_group = pygame.sprite.Group(self.name_input_box)
        self.win = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(dimx // 2, dimy // 2)
        self.mouse_pos = (0, 0)
        self.offsets = []
        self.offset = pygame.math.Vector2(0, 0)
        self.map_objects = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        self.polygons = pygame.sprite.Group()
        self.gamestate = gamestate
        self.ground = self.gamestate.ground
        self.gamestate.camera_group = self
        self.print_scores = False
        self.scores = False
        self.default_draw_floor = True
        self.draw_objects = True
        self.color_palette = [generate_random_color() for i in range(10)]
        self.last_color_palette_change = -99999999
        self.color_palette_change_cooldown = 200
        self.buttons = pygame.sprite.Group()

    def get_scores(self):
        self.print_scores = True
        re = requests.get("http://dreamlo.com/lb/664f22598f40bb12c858895d/json").content
        self.scores = json.loads(re)

    def draw_home_screen_1(self, event_list):
        self.name_input_group.update(event_list)

        self.win.fill((0, 0, 0))
        game_name = big_font.render("Seul un Blob ", 20, (255, 255, 255))
        self.win.blit(game_name, (dimx / 3, dimy // 6))
        game_name = big_font.render("peut en chasser un autre", 20, (255, 255, 255))
        self.win.blit(game_name, (dimx / 5, 2 * dimy // 4 - 200))
        game_name = big_font.render("Enter your Name then press Enter", 20, (0, 255, 0))
        self.win.blit(game_name, (300, 2 * dimy // 3))

        self.name_input_group.draw(self.win)
        pygame.display.update()

    def draw_home_screen_2(self):
        self.win.fill((0, 0, 0))
        game_name = big_font.render("Pick up Rings and Elixirs", 20, (135, 206, 235))
        self.win.blit(game_name, (dimx / 4 - 80, dimy // 4))
        pygame.display.update()

    def draw_home_screen_3(self):
        self.win.fill((0, 0, 0))
        game_name = big_font.render("Pick up Rings and Elixirs", 20, (135, 206, 235))
        self.win.blit(game_name, (dimx / 4 - 80, dimy // 4))
        game_name = big_font.render("At your own risk", 20, (75, 0, 130))
        self.win.blit(game_name, (dimx / 3 - 70, 2 * dimy // 3))
        pygame.display.update()

    def custom_draw(self, draw_floor):

        self.draw_floors(draw_floor)

        self.draw_projectiles()
        self.draw_beams()
        self.draw_polygons()
        
        self.draw_portals()
        self.draw_boss_health()
        self.draw_map_objects()
        self.draw_sprites()

        self.draw_health_bars()
        self.draw_boss_announcement()
        self.draw_xp_bar()
        self.print_messages()
        self.draw_scores()
        self.draw_buttons()
        self.draw_pause_text()
        self.draw_remaining_mobs()
        # self.draw_time()
        # self.draw_alive_shurikens()

    def draw_time(self):
        display_text(
            str(int((self.gamestate.absolute_time - self.gamestate.time)/1000)),
            dimx / 2 - 40 + self.gamestate.hero.rect.centerx,
            100 - dimy / 2 + self.gamestate.hero.rect.centery,
            self.gamestate.camera_group,
            right_align=True,
            halo=True,
        )


    def draw_projectiles(self):
        for sprite in self.projectiles.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.win.blit(sprite.image, offset_position)
            if draw_hitboxes:
                rect = sprite.rect
                pygame.draw.rect(
                    self.gamestate.win,
                    (255, 0, 0),
                    (
                        rect.left + self.offset[0],
                        rect.top + self.offset[1],
                        rect.width,
                        rect.height,
                    ),
                    3,
                )

    def draw_beams(self):
        for beam in self.beams.sprites():
            offset_start = (beam.start_x() + self.offset[0], beam.start_y() + self.offset[1])
            offset_end = (beam.end_x() + self.offset[0], beam.end_y() + self.offset[1])
            pygame.draw.line(self.gamestate.win, beam.color, offset_start, offset_end, beam.width)

    def draw_polygons(self):
        for polygon in self.polygons.sprites():
            pygame.draw.polygon(self.gamestate.win, polygon.color, polygon.points + np.array(self.offset), polygon.width)


    def draw_floors(self, draw_floor):
        if draw_floor and self.default_draw_floor:
            for floor in self.ground.sprites():
                if floor.show:
                    offset_position = floor.rect.topleft + self.offset
                    self.win.blit(floor.image, offset_position)

    def draw_portals(self):
        for portal in self.gamestate.portals.sprites():
            if (
                np.sqrt(
                    (portal.rect.centerx - self.mouse_pos[0]) ** 2
                    + (portal.rect.centery - self.mouse_pos[1]) ** 2
                )
                < 40
            ):
                portal.show_redirection()

    def draw_boss_health(self):
        for boss in self.gamestate.boss_group.sprites():
            boss.draw_health(self.gamestate.win)

    def draw_map_objects(self):
        if self.draw_objects:
            for object in self.map_objects:
                offset_position = object.rect.topleft + self.offset
                self.win.blit(object.image, offset_position)
                if draw_hitboxes:
                    rect = object.rect
                    pygame.draw.rect(
                        self.gamestate.win,
                        (255, 0, 0),
                        (
                            rect.left + self.offset[0],
                            rect.top + self.offset[1],
                            rect.width,
                            rect.height,
                        ),
                        3,
                    )

    def draw_sprites(self):
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.win.blit(sprite.image, offset_position)
            if draw_hitboxes:
                rect = sprite.rect
                pygame.draw.rect(
                    self.gamestate.win,
                    (255, 0, 0),
                    (
                        rect.left + self.offset[0],
                        rect.top + self.offset[1],
                        rect.width,
                        rect.height,
                    ),
                    3,
                )

    def draw_health_bars(self):
        if self.gamestate.draw_health_bars:
            self.gamestate.hero.draw_health(self.gamestate.win)
            for entity in self.gamestate.enemies_group.sprites():
                if entity.bool_draw_health:
                    entity.draw_health(self.gamestate.win)

    def draw_boss_announcement(self):
        if self.gamestate.prompt_boss_announcement == True:
            boss_annoucement = huge_font.render("A BIG BLOB HAS ARRIVED", 20, (255, 0, 0))
            # boss_annoucement = huge_font.render("???  CONSIGLIERE  ???", 20, (255,0,0))
            self.gamestate.win.blit(boss_annoucement, (dimx // 5, dimy // 3))

    def draw_xp_bar(self):
        self.gamestate.hero.draw_xp(self.gamestate.win)

    def print_messages(self):
        if self.gamestate.print_messages:
            for key in self.gamestate.announcements.keys():
                if self.gamestate.announcements[key][0]:
                    annoucement = normal_font.render(key, 20, self.gamestate.announcements[key][2])
                    self.gamestate.win.blit(annoucement, (20, dimy * 0.95))

    def draw_scores(self):
        if self.print_scores and self.scores:
            for i, leaderboard_entry in enumerate(self.scores["dreamlo"]["leaderboard"]["entry"]):
                if i < 10:
                    str_score = small_font.render(
                        f"{leaderboard_entry['name']:*<30}{leaderboard_entry['score']:#>10}",
                        True,
                        self.color_palette[i],
                    )
                    self.gamestate.win.blit(
                        str_score, (margin_x, margin_y + 3 * delta_y + i * delta_y)
                    )

    def draw_buttons(self):
        for button in self.buttons.sprites():
            if button.is_active:
                button.draw(self)

    def draw_remaining_mobs(self):
        if self.gamestate.draw_remaining_mobs:
            # le joueur est un monstre
            display_text(
                f"Remaining monsters : {1 + len(self.gamestate.enemies_group.sprites())}",
                -dimx / 2 + 20 + self.gamestate.hero.rect.centerx,
                -dimy / 2 + 20 + self.gamestate.hero.rect.centery,
                self,
                halo=True,
            )

    def draw_alive_shurikens(self):
        display_text(
            f"Flying / stored shurikens : {str(len(self.gamestate.shurikens.sprites()))+" / "+str(self.gamestate.hero.shuriken_ammo)}",
            -dimx / 2 + 20 + self.gamestate.hero.rect.centerx,
            -dimy / 2 + 60 + self.gamestate.hero.rect.centery,
            self,
            halo=True,
        )

    def draw_pause_text(self):
        display_text(
            "Pause/Help : P",
            dimx / 2 - 40 + self.gamestate.hero.rect.centerx,
            20 - dimy / 2 + self.gamestate.hero.rect.centery,
            self,
            right_align=True,
            halo=True,
        )

    def draw_buttons(self):
        for button in self.buttons:
            if button.is_shiny:
                border_width = 10
            else:
                border_width = 2
            pygame.draw.rect(
                self.gamestate.win,
                button.color,
                (
                    button.rect.left + self.offset[0] + border_width / 2,
                    button.rect.top + self.offset[1] + border_width / 2,
                    button.rect.width - border_width,
                    button.rect.height - border_width,
                ),
            )
            for i in range(3):
                offset_position = (
                    button.rect.topleft + self.offset + (button.random_X[i], button.random_Y[i])
                )
                if button.text == "Au feu !":
                    self.win.blit(
                        pygame.transform.rotate(button.image, button.angles[i]), offset_position
                    )
                else:
                    self.win.blit(button.image, offset_position)
            pygame.draw.rect(
                self.gamestate.win,
                button.border_color,
                (
                    button.rect.left + self.offset[0],
                    button.rect.top + self.offset[1],
                    button.rect.width,
                    button.rect.height,
                ),
                border_width,
            )

            display_text(
                button.text,
                button.rect.left + button.rect.width / 2,
                button.rect.top + button.rect.height / 2,
                self,
                color=button.text_color,
                center=True,
                halo=True,
            )

    def update(self, mouse_pos, time):
        if time - self.last_color_palette_change > self.color_palette_change_cooldown:
            self.color_palette = [generate_random_color() for _ in range(10)]
            self.last_color_palette_change = time
        hero = self.gamestate.hero
        self.ground = self.gamestate.ground

        self.offsets.append(
            pygame.math.Vector2(dimx // 2 - hero.rect.topleft[0], dimy // 2 - hero.rect.topleft[1])
        )
        if len(self.offsets) > 20:
            self.offsets.pop(0)
        self.offset = np.mean(np.array((self.offsets)))
        self.offset = pygame.math.Vector2(
            dimx // 2 - hero.rect.topleft[0], dimy // 2 - hero.rect.topleft[1]
        )
        self.mouse_pos = mouse_pos


def check_for_obstacles(entity, outside_walls=False):
    if not outside_walls:
        if entity.rect.x < start_map_x:
            entity.rect.x = start_map_x
        if entity.rect.x > end_map_x:
            entity.rect.x = end_map_x
        if entity.rect.y < start_map_y:
            entity.rect.y = start_map_y
        if entity.rect.y > end_map_y:
            entity.rect.y = end_map_y
