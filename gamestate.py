import pygame
from pygame.locals import RESIZABLE

from params import dimx, dimy


class Gamestate:
    def __init__(self):
        self.hero_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group()
        self.time = pygame.time.get_ticks()
        self.absolute_time = self.time
        self.portals = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()
        self.mobwaves = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        self.polygons = pygame.sprite.Group()
        self.shurikens = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        self.hero = None
        self.buff_enemies = False
        self.enemy_baseline_velocity = 2.5
        self.last_hero_coordinates = []
        self.draw_health_bars = True
        self.baseline_status = "Passive"
        self.n_sprites = len(self.enemies_group.sprites())
        self.mob_id = 0
        self.has_spawned_boss = False
        self.spawn_boss_thresholds = [100 * i for i in range(1, 1000)]
        #self.spawn_boss_thresholds = [0]+[100 * i for i in range(1, 1000)] # fast boss spawn for test
        self.spawn_boss_have_been_met = [False for i in range(len(self.spawn_boss_thresholds))]
        self.number_of_boss_spawns = [i for i in range(1, len(self.spawn_boss_thresholds) + 1)]
        self.prompt_boss_announcement = False
        self.date_of_last_announcement = -99999
        self.announcements = {}
        self.announcement_duration = 2500
        self.dimx = dimx
        self.dimy = dimy
        self.win = pygame.display.set_mode((dimx, dimy), RESIZABLE)
        self.print_messages = False
        self.name_has_been_entered = False
        self.draw_remaining_mobs = True
        self.fps = 60
        self.hero_is_not_paused = True
        self.mob_baselife = 100
        self.original_moblife = 100
        self.is_paused = False
        self.mouse_pos = [0, 0]
        self.buttons = pygame.sprite.Group()

    def form_the_l(self):
        n_sprites = len(self.enemies_group.sprites())
        if n_sprites > 20:
            for id, enemy in enumerate(self.enemies_group.sprites()):
                enemy.velocity = 7
                enemy.final_position = final_position(id, self.last_hero_coordinates, n_sprites)
                enemy.status = "Go to position"
            self.draw_health_bar = False
            self.baseline_status = "Go to position"
        for boss in self.boss_group.sprites():
            boss.velocity = 7

    def print_message(self, message, time, color):
        self.announcements[message] = [True, time, color]

    def drawGame(self, draw_floor=True, display_update=True):
        """Cette fonction, appelée à chaque frame, gère tout l'affichage"""

        # Réinitialisation de l'écran
        self.win.fill((0, 0, 0))
        self.win.set_alpha(25)

        # Affichage des objets dépendant de la caméra. L'ordre des affichages dans cette méthode est très important (si on représente le sol en dernier on ne verra rien)
        self.camera_group.custom_draw(draw_floor)

        # Une fois que toutes les instructions ont été données, on dit à pygame de les appliquer
        if display_update:
            pygame.display.update()

    def update(self, time, keys_pressed, mouse_pos, mouse_keys, Skillshots):
        self.absolute_time = pygame.time.get_ticks()
        self.mouse_pos = mouse_pos
        if self.hero_is_not_paused:
            self.n_sprites = len(self.enemies_group.sprites())
            if self.buff_enemies:
                for enemy in self.enemies_group.sprites():
                    enemy.velocity = 1.3 * enemy.velocity
                self.buff_enemies = False
                self.enemy_baseline_velocity = 1.3 * self.enemy_baseline_velocity

            self.time = time
            self.mob_baselife = max(1, (self.time / 100000) ** 0.5) * self.original_moblife
            self.hero_group.update(time, keys_pressed, mouse_pos, mouse_keys)
            self.beams.update()
            self.polygons.update()
            self.shurikens.update(time)
            self.enemies_group.update(time)
            self.boss_group.update(time)
            self.obstacles.update(time)
            self.mobwaves.update(time)
            self.portals.update(Skillshots, mouse_pos, time)
            self.ground.update(self.hero.rect.centerx, self.hero.rect.centery, time)
            self.number_of_monsters_killed = self.hero.kills

            for threshold_index, threshold in enumerate(self.spawn_boss_thresholds):
                if not self.spawn_boss_have_been_met[threshold_index]:
                    if self.number_of_monsters_killed >= threshold:
                        self.prompt_boss_announcement = True
                        self.date_of_last_announcement = time
                        for i in range(self.number_of_boss_spawns[threshold_index]):
                            offset = i * 300
                            self.spawn_boss(offset)
                        self.spawn_boss_have_been_met[threshold_index] = True

            if time - self.date_of_last_announcement > 2000:
                self.prompt_boss_announcement = False
            for key in self.announcements.keys():
                if time > self.announcements[key][1] + self.announcement_duration:
                    self.announcements[key][0] = False

    def spawn_boss(self, offset):
        if not self.has_spawned_boss:
            self.has_spawned_boss = True
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load("Assets/Music/Vincenzo.mp3")
            pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=750)
            
        from boss import Boss

        boss = Boss(self, self.camera_group)

        boss.rect.centerx += offset
        self.hero.potential_targets.add(boss)

    def stop_printing_messages(self):
        self.print_messages = False


def final_position(id, last_coordinates, n_sprites):
    ymin = last_coordinates[1] - 600
    ymax = ymin + 700
    xmin = last_coordinates[0] - 100
    xmax = xmin + 300
    if id < int(0.3 * n_sprites):
        x = xmin + (xmax - xmin) * (1 - id / (0.3 * n_sprites))
        y = ymax
    else:
        x = xmin
        y = ymax + (ymin - ymax) * (id - int(0.3 * n_sprites)) / (
            n_sprites - 1 - int(0.3) * n_sprites
        )
    return (x, y)
