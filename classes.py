import pygame


class Vecteur:
    """Un vecteur mathematique
    Deux manières de le créer:
    - avec sa norme en x et en y (float/int)
    - avec deux coordonnées de points A et B (tuple)"""

    def __init__(self, **kwargs):
        if "x" in kwargs.keys() and "y" in kwargs.keys():
            assert isinstance(kwargs['x'], (int, float)) and isinstance(
                kwargs['y'], (int, float)), "x et y doivent être des nombres valides"
            self.x = kwargs['x']
            self.y = kwargs['y']
        elif "A" in kwargs.keys() and "B" in kwargs.keys():
            assert isinstance(kwargs['A'], (tuple, list)) and isinstance(
                kwargs['B'], (tuple, list)), "A et B doivent être des tuples"
            self.x = abs(kwargs['A'][0] - kwargs['B'][0])/2
            self.y = abs(kwargs['A'][1] - kwargs['B'][1])/2
        else:
            raise TypeError("Missing arguments")


class Voiture:
    """Représente une voiture
    color is a pygame.Color used to represent the car"""

    def __init__(self, color: pygame.Color = pygame.Color(255, 0, 0)):
        self.color = color
        self.position = [0, 0]

    def set_position(self, x: int, y: int):
        self.position = [x, y]
