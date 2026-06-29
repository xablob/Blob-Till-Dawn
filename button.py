import numpy as np
import pygame

from camera import dimx
from gamestate import dimx, dimy
from spritesheet import lightning_spritesheet
from utilities import reshape

lightning_image = reshape(lightning_spritesheet.image_at([0, 2000, 1000, 1000]).convert_alpha(), 8)
bubble_image = reshape(pygame.image.load("Assets/Water__05.png").convert_alpha(), 2.2)
stats_image = reshape(
    pygame.image.load("Assets/lightning_spritesheet/ajouter.png").convert_alpha(), 6.5
)
fire_image = pygame.transform.rotate(
    reshape(pygame.image.load("Assets/Fireball/fireballupdown.png").convert_alpha(), 2), 90
)

possible_texts = ["Plus de bulles !", "Wind guide you", "Au feu !", "Plein de stats"]
possible_colors = {
    "Plus de bulles !": (0, 255, 255),
    "Wind guide you": (255, 255, 255),
    "Au feu !": (223, 109, 20),
    "Plein de stats": (0, 180, 0),
}
possible_images = {
    "Plus de bulles !": bubble_image,
    "Wind guide you": lightning_image,
    "Au feu !": fire_image,
    "Plein de stats": stats_image,
}


class Button(pygame.sprite.Sprite):
    def __init__(
        self,
        gamestate,
        left,
        top,
        width,
        height,
        camera_group,
        hero,
        button_group,
        button_type="Upgrade",
    ):
        super().__init__(gamestate.buttons)
        self.rect = pygame.rect.Rect(
            hero.rect.left + left - dimx / 2, hero.rect.top + top - dimy / 2, width, height
        )
        # self.rect = pygame.rect.Rect(hero.rect.left, hero.rect.top, width, height)
        self.is_active = True
        self.is_shiny = True
        self.color = np.random.randint(0, 255, 3)
        self.color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        self.text = possible_texts[np.random.randint(0, len(possible_texts))]
        self.text_color = possible_colors[self.text]
        camera_group.buttons.add(self)
        self.hero = hero
        self.button_type = button_type
        self.button_group = button_group
        self.button_group.add(self)
        self.has_been_activated = False
        self.image = possible_images[self.text]
        self.gamestate = gamestate
        self.gamestate.camera_group.buttons.add(self)
        self.random_X = np.random.uniform(0, self.rect.width * 0.8, 3)
        self.random_Y = np.random.uniform(0, self.rect.height * 0.8, 3)
        if self.text == "Au feu !":
            self.angles = np.random.randint(0, 360, 3)
        # self.random_X = [0, 0, 0]
        # self.random_Y = [0, 0, 0]

    def activate(self):
        if self.button_type == "Upgrade":
            hero = self.hero
            text = self.text
            if text == "Plus de bulles !":
                hero.skill_ranks["Bulles"] += 1
                hero.number_of_proj += 1
                hero.number_of_splits += 2
            elif text == "Wind guide you":
                hero.velocity += 0.3 * hero.original_velocity
            elif text == "Au feu !":
                hero.skill_ranks["Rotating Orbs"] += 1
                hero.upgrade_orbs()
                hero.orb_level += 1
                hero.tp_distance += 10
            elif text == "Que du bonheur":
                hero.cooldowns["Fireball"] = 0.8 * hero.cooldowns["Fireball"]
                hero.attack_power = 1.1 * hero.attack_power
                hero.life += 2
                hero.max_life += 2
            elif text == "Ninja !":
                hero.skill_ranks["Shuriken"] += 1
            hero.update_skills()
        self.has_been_activated = True

    def is_hovered(self, mouse_pos):
        if (
            self.rect.left <= mouse_pos[0]
            and self.rect.left + self.rect.width >= mouse_pos[0]
            and self.rect.top <= mouse_pos[1]
            and self.rect.top + self.rect.height >= mouse_pos[1]
        ):
            self.is_shiny = True
            return True
        else:
            self.is_shiny = False
            return False

    def update(self, camera_group):
        # print("im trying")
        is_hovered = self.is_hovered(pygame.mouse.get_pos() - camera_group.offset)
        if is_hovered:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 = clic gauche
                    # print("Bouton cliqué !")
                    self.activate()
        if self.has_been_activated:
            for button in self.button_group.sprites():
                if button != self:
                    # print("je suis un autre bouton")
                    button.kill()
            self.kill()
            self.gamestate.is_paused = False
