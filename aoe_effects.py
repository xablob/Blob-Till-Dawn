import numpy as np
from utilities import generate_random_color, slightly_change_color, get_barycentre, get_angle, Droite
import pygame

class Rectangular_beam(pygame.sprite.Sprite):
    def __init__(self, gamestate, length, width, caster, angle, x_center, y_center, rotation_speed = 0):
        super().__init__(gamestate.beams, gamestate.camera_group.beams)
        self.centerx = x_center
        self.centery = y_center
        self.caster = caster
        self.angle = angle
        self.length = length
        self.width = width
        self.color = generate_random_color()
        self.rotation_speed = rotation_speed
        self.potential_targets = self.caster.potential_targets
        
    def update(self):
        self.centerx = self.caster.rect.centerx
        self.centery = self.caster.rect.centery
        self.color = slightly_change_color(self.color)
        self.angle += self.rotation_speed
        for entity in self.potential_targets:
            if self.is_colliding_with(entity):
                self.apply(entity)

    def apply(self, entity):
        print("Une cible a été touchée")


    def start_x(self):
        return self.centerx - self.length * 0.5 * np.cos(self.angle)

    def start_y(self):
        return self.centery - self.length * 0.5 * np.sin(self.angle)

    def end_x(self):
        return self.centerx + self.length * 0.5 * np.cos(self.angle)

    def end_y(self):
        return self.centery + self.length*0.5*np.sin(self.angle)
    
    def is_colliding_with(self, entity):
        pass

    def equations_décrivant_la_zone(self):
        """Obtient les n équations de droites à partir des n points du polygone"""
        
    
    def polygon(self):
        start = (self.start_x(), self.start_y())
        end = (self.end_x(), self.end_y())
        x1 = start[0] - self.width * 0.5 * np.cos(self.angle + np.pi / 2)
        y1 = start[1] - self.width * 0.5 * np.sin(self.angle + np.pi / 2)
        x2 = start[0] + self.width * 0.5 * np.cos(self.angle + np.pi / 2)
        y2 = start[1] + self.width * 0.5 * np.sin(self.angle + np.pi / 2)
        x3 = end[0] - self.width * 0.5 * np.cos(self.angle + np.pi / 2)
        y3 = end[1] - self.width * 0.5 * np.sin(self.angle + np.pi / 2)
        x4 = end[0] + self.width * 0.5 * np.cos(self.angle + np.pi / 2)
        y4 = end[1] + self.width * 0.5 * np.sin(self.angle + np.pi / 2)
        return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    


class Polygon_effect(pygame.sprite.Sprite):
    def __init__(self, gamestate, caster, points, width = 0, rotation_speed = 0):
        super().__init__(gamestate.polygons, gamestate.camera_group.polygons)
        self.points = points
        float_array = []
        for i, points in enumerate(self.points):
            float_tuple = (float(self.points[i][0]), float(self.points[i][1]))
            float_array.append(float_tuple)
        float_array = np.array(float_array, dtype = "float")
        self.points = float_array
        self.caster = caster
        self.color = generate_random_color()
        self.rotation_speed = rotation_speed
        #self.potential_targets = self.caster.potential_targets
        self.potential_targets = []
        self.barycentre = get_barycentre(self.points)
        self.width = width
        
    def print_first_point(self):
        print("Points : ", [(point[0], point[1]) for point in self.points])
    def update(self):
        self.color = slightly_change_color(self.color)
        self.rotate()
        for entity in self.potential_targets:
            if self.is_colliding_with(entity):
                self.apply(entity)

    def rotate(self) :
        for i, point in enumerate(self.points):

            old_x, old_y = point[0], point[1]
            
            old_angle = get_angle((old_x - self.barycentre[0], old_y - self.barycentre[1]))
            old_radius = ((old_x - self.barycentre[0])**2 + (old_y - self.barycentre[1])**2)**0.5

            new_angle = old_angle + self.rotation_speed

            new_x = self.barycentre[0] + old_radius * np.cos(new_angle)
            new_y = self.barycentre[1] + old_radius * np.sin(new_angle)
            
            self.points[i] = (new_x, new_y)


    def apply(self, entity):
        print("Une cible a été touchée")

    
    def is_colliding_with(entity):
        """Teste la position de l'entité vs chacune des équations de droites"""
        """Pour les droites obliques  , on part de l'axiome que les points ont été renseignés en sens horaire"""

    def equations_décrivant_la_zone(self):
        """Obtient les n équations de droites à partir des n points du polygone"""
        n_points = len(self.points)
        points = self.points
        droites = []
        for index_point in range(n_points):
            droite = Droite(points[index_point], points[(index_point+1)%n_points]) #conditions aux limites périodiques
            droites.append(droite)
        return droites

        


    

        
