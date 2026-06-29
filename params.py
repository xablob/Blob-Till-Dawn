# Valeurs utilisées pour réguler le spawn des monstres
from tkinter import Tk

last_spawn = -99999  # date de la dernière vague
spawn_cd = 10000  # intervalle entre deux vagues


# Ce booléen sert à afficher les instructions pendant que le jeu est en pause
draw_instructions = False

# Permet d'activer ou non le spawn des monstres
allow_spawn = True

# Choix de la couleur principale d'écriture
writing_color = (255, 255, 255)

# Pour que les unités ne soient pas représentées par des rectangles de couleur...
use_images = True

# Nombre initial de monstres par vague
mobs_per_wave = 1

# Dimensions et position de la barre d'xp
xp_bar_height = 20
xp_bar_length = 800
offset_xp_bar_y = 20

xp_threshold = 3

color_period = 1000

gold_color = (212, 175, 55)
gold_color = (153, 101, 21)
gold_color = (50, 50, 50)
# gold_color = (51,26,0)
xp_color = (150, 150, 150)


# Pour ne pas que les menus soient tous skippés sur une pression d'Enter
last_menu_switch = -1000
menu_switch_cooldown = 300

# Gestion de la pause
pause_cd = 200  # intervalle entre deux activations du bouton de pause, sinon ça bug
last_pause = -9999  # date de la dernière pause

dimx = 1 * Tk().winfo_screenwidth()
dimy = 1 * Tk().winfo_screenheight()


draw_hitboxes = False


start_map_x = -3 * dimx
start_map_y = -3 * dimy
end_map_x = 3 * dimx
end_map_y = 3 * dimy

coeff_resize_x = dimx / 1680
coeff_resize_y = dimy / 1050


xp_bar_centerx = dimx / 2
xp_bar_centery = dimy - xp_bar_height / 2 - offset_xp_bar_y
xp_bar_topleft_x = xp_bar_centerx - xp_bar_length / 2
xp_bar_topleft_y = xp_bar_centery - xp_bar_height / 2
