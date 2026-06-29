import pygame


class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, gamestate, x, y, w, font):
        super().__init__()
        self.color = (255, 255, 255)
        self.backcolor = None
        self.pos = (x, y)
        self.width = w
        self.font = font
        self.active = True
        self.text = ""
        self.gamestate = gamestate
        self.render_text()

    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface(
            (max(self.width, t_surf.get_width() + 10), t_surf.get_height() + 20),
            pygame.SRCALPHA,
        )
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, event_list):
        for event in event_list:
            # if event.type == pygame.MOUSEBUTTONDOWN and not self.active:
            #     self.active = self.rect.collidepoint(event.pos)
            #     print("yes")
            if event.type == pygame.KEYDOWN and self.active:
                # if event.key == pygame.K_RETURN:
                #     self.active = False
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.render_text()
                if event.key == pygame.K_RETURN:
                    self.gamestate.hero.leaderboard_name = self.text.strip()
                    while self.text[0] == " ":
                        self.text = self.text[1:]
                    self.kill()
                    self.gamestate.name_has_been_entered = True


# font = pygame.font.SysFont(None, 100)
# text_input_box = TextInputBox(50, 50, 400, font)
# group = pygame.sprite.Group(text_input_box)
