import pygame


class Vector:
    """Un vecteur mathematique
    Deux manieres de le creer:
    - avec sa norme en x et en y (float/int)
    - avec deux coordonnees de points A et B (tuple)"""

    def __init__(self, **kwargs):
        if "x" in kwargs.keys() and "y" in kwargs.keys():
            assert isinstance(kwargs['x'], (int, float)) and isinstance(
                kwargs['y'], (int, float)), "x et y doivent être des nombres valides"
            self.x = kwargs['x']
            self.y = kwargs['y']
        elif "A" in kwargs.keys() and "B" in kwargs.keys():
            assert isinstance(kwargs['A'], (tuple, list)) and isinstance(
                kwargs['B'], (tuple, list)) and len(kwargs['A']) == len(kwargs['B']) == 2, "A et B doivent être des tuples de longueur 2"
            self.x = abs(kwargs['A'][0] - kwargs['B'][0])/2
            self.y = abs(kwargs['A'][1] - kwargs['B'][1])/2
        else:
            raise TypeError("Missing arguments")


class Car:
    """Represente une voiture
    color represente la couleur de la voiture, de type pygame.Color"""

    def __init__(self, color: pygame.Color = pygame.Color(255, 0, 0)):
        """Initialise la voiture
        - color (pygame.Color): couleur de la voiture [par défaut rouge]"""
        self.color = color
        self.position = [0, 0]

    def set_position(self, x: int, y: int):
        """Modifie la position absolue de la voiture
        - x (int): nouvelle position de la voiture sur l'axe X (abscisse)
        - y (int): nouvelle position de la voiture sur l'axe Y (ordonnée)"""
        self.position = [x, y]

    def apply_vector(self, vector: Vector):
        """Applique un vecteur à la position de la voiture
        - vector (Vector): vecteur à appliquer"""
        self.position[0] += vector.x
        self.position[1] += vector.y


class Border:
    """Represente une bordure de circuit
    Ligne droite allant de A(x,y) a B(x,y)"""

    def __init__(self, A: tuple, B: tuple, color: pygame.Color = pygame.Color(96, 96, 96)):
        assert isinstance(A, (tuple, list)) and isinstance(B, (tuple, list)) and len(
            A) == len(B) == 2, "A et B doivent être des tuples de longueur 2"
        self.color = color
        self.start = A
        self.end = B
