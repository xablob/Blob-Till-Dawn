import pygame

from fonts import delta_y, display_text, margin_x, margin_y
from game_init import gamestate, hero
from params import dimx, dimy
from projectile import Skillshots, entity_targeted_projectiles


def draw_pause_screen(debug=True):
    """Utilisée pendant les pauses, cette fonction affiche sur la fenêtre win toutes les commandes"""
    if debug:
        debug_offset_y = 2 * margin_y

        display_text(
            f"Number of proj {hero.number_of_proj}",
            dimx - margin_x,
            debug_offset_y,
            right_align=True,
        )
        display_text(
            f"Cooldown {hero.cooldowns['Fireball']}",
            dimx - margin_x,
            debug_offset_y + delta_y,
            right_align=True,
        )
        display_text(
            f"Attack power {hero.attack_power}",
            dimx - margin_x,
            debug_offset_y + 2 * delta_y,
            right_align=True,
        )
        display_text(
            f"Attack total {hero.attack_power * hero.number_of_proj}",
            dimx - margin_x,
            debug_offset_y + 3 * delta_y,
            right_align=True,
        )
        display_text(
            f" Time : {pygame.time.get_ticks() / 1000:>5.0f}",
            dimx - margin_x,
            debug_offset_y + 4 * delta_y,
            right_align=True,
        )
        display_text(
            f"{len(gamestate.enemies_group.sprites()):>6} Monsters ",
            dimx - margin_x,
            debug_offset_y + 5 * delta_y,
            right_align=True,
        )
        display_text(
            f"N projectiles : {len(entity_targeted_projectiles.sprites()) + len(Skillshots.sprites())}",
            dimx - margin_x,
            debug_offset_y + 6 * delta_y,
            right_align=True,
        )

    # Left click
    left_click_txt_x_size = display_text(
        "Left click to ", 0.5 * dimx, 0.7 * dimy - 3 * delta_y, center=True
    )[0]
    display_text(
        "RAIN FIRE",
        0.5 * dimx + left_click_txt_x_size // 2,
        0.7 * dimy - 3 * delta_y,
        (255, 165, 0),
    )  # orange
    # Right click
    right_click_txt_x_size = display_text(
        "A or right click to spawn a ", 0.5 * dimx, 0.7 * dimy - 2 * delta_y, center=True
    )[0]
    display_text(
        "Portal",
        0.5 * dimx + right_click_txt_x_size // 2,
        0.7 * dimy - 2 * delta_y,
        (135, 206, 235),
    )  # aqua blue
    # Erase portals
    erase_portals_txt_x_size = display_text(
        "N to erase ", 0.5 * dimx, 0.7 * dimy - delta_y, center=True
    )[0]
    display_text(
        "Portals", 0.5 * dimx + erase_portals_txt_x_size // 2, 0.7 * dimy - delta_y, (135, 206, 235)
    )  # aqua blue
    # Pause menu
    display_text("Press P to Start/Pause", 0.5 * dimx, 0.7 * dimy, center=True)
    # Rings / potions
    display_text(
        "Pick up rings and potions at your own risk",
        0.5 * dimx,
        0.7 * dimy + delta_y,
        (75, 0, 130),
        center=True,
    )  # purple
    # Teleport
    teleport_txt_x_size = display_text(
        "Space to ", 0.5 * dimx, 0.7 * dimy + 2 * delta_y, center=True
    )[0]
    display_text(
        "Teleport", 0.5 * dimx + teleport_txt_x_size // 2, 0.7 * dimy + 2 * delta_y, (15, 15, 15)
    )  # almost black
    # Ctrl
    display_text(
        "Ctrl to LEAVE BEHIND A FRAGMENT OF YOUR SOUL",
        0.5 * dimx,
        0.7 * dimy + 3 * delta_y,
        (255, 0, 0),
        center=True,
    )  # red
