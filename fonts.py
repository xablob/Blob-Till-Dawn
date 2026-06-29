import pygame

from params import dimx, dimy, writing_color

pygame.font.init()
font_sizes = [30, 50, 75, 100]
scaling = min(dimy / 1000, 1)
small_font = pygame.font.Font("Assets/BreatheFire-65pg.ttf", int(scaling * font_sizes[0]))
normal_font = pygame.font.Font("Assets/BreatheFire-65pg.ttf", int(scaling * font_sizes[1]))
big_font = pygame.font.Font("Assets/BreatheFire-65pg.ttf", int(scaling * font_sizes[2]))
huge_font = pygame.font.Font("Assets/BreatheFire-65pg.ttf", int(scaling * font_sizes[3]))

# Boundaries inside which text must be printed
margin_x = 2 * font_sizes[0]
margin_y = 2 * font_sizes[0]

# Space occupied by a single character
delta_x, delta_y = normal_font.size("A")


def display_text(
    text,
    pos_x,
    pos_y,
    camera_group,
    color=writing_color,
    font=normal_font,
    right_align=False,
    center=False,
    halo=False,
    win=pygame.display.set_mode((dimx, dimy), pygame.RESIZABLE),
):
    """Display text on screen at given position and color.
    Default color is writing_color (white).
    Default behaviour : start writing text at pos_x
    right align = True => end print at pos_x
    center = True => halfway print at pos_x
    Return space occupied by given text"""
    if right_align:
        # shift pos_x accordingly
        pos_x -= font.size(text)[0]
    if center:
        # shift pos_x accordingly
        pos_x -= font.size(text)[0] // 2
    text_surface = font.render(text, True, color)
    if halo:
        outline_color = (0, 0, 0)
        outline_thickness = 2
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx**2 + dy**2 <= outline_thickness**2:  # cercle
                    win.blit(
                        font.render(text, True, outline_color),
                        (
                            pos_x + camera_group.offset[0] + dx + outline_thickness,
                            pos_y + camera_group.offset[1] + dy + outline_thickness,
                        ),
                    )
    win.blit(text_surface, (pos_x + camera_group.offset[0], pos_y + camera_group.offset[1]))
    return text_surface.get_size()
