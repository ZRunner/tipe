import pygame
import math

vector = pygame.math.Vector2


def lineRayIntersectionPoint(rayOrigin: tuple, rayDirection: tuple, point1: tuple, point2: tuple):
    """Donne le vecteur allant de l'origine vers le point d'intersection
    Source: http://bit.ly/2VfSFOV
    Tous les arguments doivent être de la forme (x,y)"""
    # Convert to vectors
    rayOrigin = vector(rayOrigin)
    rayDirection = vector(rayDirection).normalize()
    point1 = vector(point1)
    point2 = vector(point2)

    # Ray-Line Segment Intersection Test in 2D
    # http://bit.ly/1CoxdrG
    v1 = rayOrigin - point1
    v2 = point2 - point1
    v3 = vector([-rayDirection[1], rayDirection[0]])
    try:
        t1 = v2.cross(v1) / v2.dot(v3)
        t2 = v1.dot(v3) / v2.dot(v3)
    except ZeroDivisionError:
        return []
    if t1 >= 0.0 and t2 >= 0.0 and t2 <= 1.0:
        return [rayOrigin + t1 * rayDirection]
    return []


class Car:
    """Represente une voiture
    color represente la couleur de la voiture, de type pygame.Color"""

    def __init__(self, color: pygame.Color = pygame.Color(255, 0, 0), abs_rotation: float = -90):
        """Initialise la voiture
        - color (pygame.Color): couleur de la voiture [par défaut rouge]
        - abs_rotation (float): rotation par rapport au plan de la voiture [par défaut sud]"""
        self.color = color
        self.position = [0, 0]
        self.abs_rotation = abs_rotation

    def set_position(self, x: int, y: int):
        """Modifie la position absolue de la voiture
        - x (int): nouvelle position de la voiture sur l'axe X (abscisse)
        - y (int): nouvelle position de la voiture sur l'axe Y (ordonnée)"""
        self.position = [x, y]

    def apply_vector(self, vector: pygame.math.Vector2):
        """Applique un vecteur à la position de la voiture
        - vector (Vector): vecteur à appliquer"""
        self.position[0] += vector.x
        self.position[1] += vector.y

    def raytrace(self, angle: int, circuit: list, max_distance: int = 200, use_absolute_angle: bool = False, return_real_distance: bool = False):
        """Vérifie si le rayon d'angle donné rencontre un mur avant une certaine distance
        - angle (int): angle du rayon en degrés, 0 étant l'avant de la voiture
        - circuit (list): liste de tous les murs à prendre en compte, de type Border
        - max_distance (int): distance maximum à prendre en compte [par défaut 200]
        - use_absolute_angle (bool): si l'angle donné est relatif au plan (1) ou à la voiture (0) [par défaut False]
        - return_real_distance (bool): si la valeur retournée doit être la distance réelle, et non entre 0 et 1 [par défaut False]

        Retourne un float entre 0 et 1, 0 étant une collision immédiate et 1 à la distance maximum, ou -1 si aucune collision"""
        assert all([isinstance(x, Border) for x in circuit]), "La liste du circuit ne doit contenir que des objets de type Border"
        if not use_absolute_angle:
            angle = self.abs_rotation + angle
        angle = math.radians(angle)
        direction = vector(round(math.cos(angle), 5),
                           round(math.sin(angle), 5))
        distances = [lineRayIntersectionPoint(self.position, direction, (
            line.start[0], line.start[1]), (line.end[0], line.end[1])) for line in circuit]
        distances = [x[0].length() for x in distances if len(x) > 0]
        if len(distances) == 0:
            return -1
        shortest_distance = min(distances)
        if shortest_distance > max_distance:
            return -1
        if return_real_distance:
            return shortest_distance
        return shortest_distance/max_distance

    def direction_vector(self):
        """Renvoie un vecteur unitaire dans la direction de self.abs_rotation"""
        return vector(math.cos(math.radians(self.abs_rotation)) - math.sin(math.radians(self.abs_rotation)), 
                      math.sin(math.radians(self.abs_rotation)) + math.cos(math.radians(self.abs_rotation)))


class Border:
    """Represente une bordure de circuit
    Ligne droite allant de A(x,y) a B(x,y)"""

    def __init__(self, A: tuple, B: tuple, color: pygame.Color = pygame.Color(96, 96, 96)):
        assert isinstance(A, (tuple, list)) and isinstance(B, (tuple, list)) and len(A) == len(B) == 2, "A et B doivent être des tuples de longueur 2"
        self.color = color
        self.start = A
        self.end = B


# # -- Tests de raytracing -- #
# borders = [Border((8,10),(-2,10)), Border((5,9),(-6,7))]
# car = Car(abs_rotation=60)
# car.set_position(1,0.5)
# print(car.raytrace(0, borders, max_distance=12, return_real_distance=True))
