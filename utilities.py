import numpy as np
import pygame


def reshape(image, coeff):
    dim = image.get_size()
    image = pygame.transform.scale(image, [dim[0] / coeff, dim[1] / coeff])
    return image


def get_angle(direction):
    if direction[0] > 0 and direction[1] < 0:
        angle_base = np.arctan(direction[1] / direction[0])
    elif direction[0] > 0 and direction[1] >= 0:
        angle_base = np.arctan(direction[1] / direction[0])
    elif direction[0] < 0 and direction[1] < 0:
        angle_base = np.arctan(direction[1] / direction[0]) - np.pi
    elif direction[0] < 0 and direction[1] >= 0:
        angle_base = np.pi + np.arctan(direction[1] / direction[0])
    elif direction[0] == 0:
        if direction[1] > 0:
            angle_base = np.pi / 2
        else:
            angle_base = -np.pi / 2
    else:
        return np.random.uniform(0, 2 * np.pi)
    return angle_base


def rotate(image, rect, angle):
    """Rotate the image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


def is_entity(element):
    if (
        type(element) == "Enemy"
        or type(element) == "Hero"
        or type(element) == "Minion"
        or type(element) == "Totem"
    ):
        return True
    else:
        return False


def draw_rect(entity, win):
    topleft = entity.rect.topleft + entity.offset
    x, y = topleft
    width, height = entity.rect.width, entity.rect.height
    pygame.draw.line(win, (255, 0, 0), (x, y), (x + width, y), 5)
    pygame.draw.line(win, (255, 0, 0), (x, y + height), (x + width, y + height), 5)
    pygame.draw.line(win, (255, 0, 0), (x, y), (x, y + height), 5)
    pygame.draw.line(win, (255, 0, 0), (x + width, y), (x + width, y + height), 5)


def reshape_until(image, size):
    dim = image.get_size()
    image = pygame.transform.scale(image, size)
    return image


def reshape_1D(image, coeff, dimension):
    dim = image.get_size()
    if dimension == 0:
        image = pygame.transform.scale(image, [dim[0] / coeff, dim[1]])
    else:
        image = pygame.transform.scale(image, [dim[0], dim[1] / coeff])
    return image


def get_signe(number):
    if number >= 0:
        return 1
    else:
        return -1


def generate_map_ids(n_tiles_x, n_tiles_y):
    a, b, c, d, e = np.random.uniform(-5, 5, 5)
    map = np.zeros[(n_tiles_x, n_tiles_y)]
    for i in range(n_tiles_x):
        for j in range(n_tiles_y):
            map[i][j] = int()

class Droite:
    def __init__(self, point1, point2):
        pente, ordonnee = equation_de_droite(point1, point2)
        if pente:
            self.droite_type = "oblique"
            self.pente = pente
            self.ordonnee = ordonnee
        else:
            self.droite_type = "verticale"
            self.abcisse = ordonnee

def equation_de_droite(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    if x1 != x2 :
        pente = (y2 - y1)/(x2 - x1)
        ordonnee_a_lorigine = y1 - pente*x1
        return (pente, ordonnee_a_lorigine)
    else:
        abcisse = x1
        return (False, abcisse)
        

def harmonize(tiles_id):
    n_tiles_x, n_tiles_y = len(tiles_id), len(tiles_id[0])
    for i in range(n_tiles_x):
        for j in range(n_tiles_y):
            p = np.random.uniform(0, 1)
            if p < 0.3:
                # Faire une tache uniforme autour de i, j
                length_x = np.random.randint(1, 6)
                length_y = np.random.randint(1, 6)
                for k in range(length_x):
                    for l in range(length_y):
                        if 0 <= i + k <= n_tiles_x - 1 and 0 <= j + l <= n_tiles_y - 1:
                            tiles_id[i + k][j + l] = tiles_id[i][j]
                        elif 0 <= i - k <= n_tiles_x - 1 and 0 <= j - l <= n_tiles_y - 1:
                            tiles_id[i - k][j - l] = tiles_id[i][j]
                        elif 0 <= i + k <= n_tiles_x - 1 and 0 <= j - l <= n_tiles_y - 1:
                            tiles_id[i + k][j - l] = tiles_id[i][j]
                        elif 0 <= i - k <= n_tiles_x - 1 and 0 <= j + l <= n_tiles_y - 1:
                            tiles_id[i - k][j + l] = tiles_id[i][j]


def generate_random_color():
    return (
        np.random.randint(0, 255),
        np.random.randint(0, 255),
        np.random.randint(0, 255),
    )


def slightly_change_color(color):
    red, green, blue = color[0], color[1], color[2]
    amplitude = 5
    delta = np.random.uniform(-amplitude, amplitude, 3)
    return ((red + delta[0]) % 255, (green + delta[1]) % 255, (blue + delta[2]) % 255)


def old_replace_outside_obstacle(obstacle, entity):
    x1, y1 = entity.rect.center[0], entity.rect.center[1]
    x2, y2 = obstacle.rect.topleft[0], obstacle.rect.topleft[1]
    distance_to_left = abs(x2 - x1)
    distance_to_right = abs(x2 + obstacle.rect.width - x1)
    distance_to_top = abs(y2 - y1)
    distance_to_bottom = abs(y2 + obstacle.rect.height - y1)
    min_dist = min(distance_to_left, distance_to_right, distance_to_bottom, distance_to_top)
    print(x1, y1, x2, y2)
    print(distance_to_bottom, distance_to_left, distance_to_right, distance_to_top)
    if min_dist == distance_to_top:
        print("top")
        entity.rect.topleft = (entity.rect.topleft[0], y2 - entity.rect.height - 5)
    elif min_dist == distance_to_bottom:
        print("bottom")
        entity.rect.topleft = (entity.rect.topleft[0], y2 + obstacle.rect.height + 5)
    elif min_dist == distance_to_right:
        print("right")
        entity.rect.topleft = (x2 + obstacle.rect.width + 5, entity.rect.topleft[1])
    else:
        print("left")
        assert min_dist == distance_to_left
        entity.rect.topleft = (x2 - entity.rect.width - 5, entity.rect.topleft[1])


def replace_outside_obstacle(obstacle, entity):
    x1, y1 = entity.rect.center[0], entity.rect.center[1]
    x2, y2 = obstacle.rect.topleft[0], obstacle.rect.topleft[1]
    entity.rect.centerx = entity.last_x
    if entity.is_colliding_with(obstacle):
        entity.rect.centerx = x1
        entity.rect.centery = entity.last_y


class Event_on_health_threshold(pygame.sprite.Sprite):
    def __init__(self, entity, threshold, activation):
        super().__init__(entity.events)
        self.entity = entity
        self.threshold = threshold
        self.activation = activation

    def update(self):
        current_threshold = self.entity.life / self.entity.max_life
        if current_threshold < self.threshold:
            self.activate()
            self.kill()

    def activate(self):
        self.activation(self.entity)

        
def get_barycentre(points):
    x = 0
    y = 0
    for point in points:
        x += point[0]
        y += point[1]
    x = x/len(points)
    y = y/len(points)
    return (x,y)