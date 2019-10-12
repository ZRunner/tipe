from math import sqrt
from random import randint
from classes import Border
import settings


def _ligne_droite(n: int, a: tuple, b: tuple) -> tuple:
    """
    Crée une ligne droite et retourne les bordules du chemin aini que les nouveaux points a et b
    - n (int): nombre de pixels de la ligne droite
    - a et b (tuple de deux entiers): coordonnées du début du chemin
    Retourne : [Bordure 1, Bordure 2, point a, point b]
    """
    x1, x2, y1, y2 = a(0), b(0), a(1), b(1)
    x, y = x1-x2, y1-y2
    if x < 0:
        return (Border((x1, y1), (x1, y1-n)), Border((x2, y2), (x2, y2-n)), (x1, y1-n), (x2, y2-n))
    if x > 0:
        return (Border((x1, y1), (x1, y1+n)), Border((x2, y2), (x2, y2+n)), (x1, y1+n), (x2, y2+n))
    if y < 0:
        return (Border((x1, y1), (x1+n, y1)), Border((x2, y2), (x2+n, y2)), (x1+n, y1), (x2+n, y2))
    else:
        return (Border((x1, y1), (x1-n, y1)), Border((x2, y2), (x2-n, y2)), (x1-n, y1), (x2-n, y2))


def _virage(d, a, b):
    """
    Crée un _virage et retourne les bordules du chemin aini que les nouveaux points a et b
    - d (int): direction du _virage (0=droite,1=gauche)
    - a et b (tuple de deux entiers): coordonnées des bords en entrée de _virage
    Retourne : [Bordure 1, Bordure 2, point a, point b]
    """
    taille = settings.screen_size[0]
    x1, x2, y1, y2 = a(0), b(0), a(1), b(1)
    n = sqrt((x1-x2) ^ 2+(y1-y2) ^ 2)
    x, y = x1-x2, y1-y2
    if d == 0:
        if x < 0:  # renvoie les trait et la position des deux points d'arrivée
            if x2 > int(4*(taille/20)*sqrt(2)/2):
                return (Border((x1, y1), (x1+(3*n/2), y1-(3*n/2))), Border((x2, y2), (x2+(n/2), y2-(n/2))), (x2+(3*n/2), y2-(3*n/2)), (x2+(n/2), y2-(n/2)))
            else:
                # si la route est trop pret du bords de l'ecran on fait le _virage dans l'autre sens
                return(_virage(1, a, b))
        if x > 0:
            if x2 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1-(3*n/2), y1+(3*n/2))), Border((x2, y2), (x2-(n/2), y2+(n/2))), (x1-(3*n/2), y1+(3*n/2)), (x2-(n/2), y2+(n/2)))
            else:
                return(_virage(1, a, b))
        if y < 0:
            if y2 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1-(3*n/2), y1-(3*n/2))), Border((x2, y2), (x2-(n/2), y2-(n/2))), (x1-(3*n/2), y1-(3*n/2)), (x2-(n/2), y2-(n/2)))
            else:
                return(_virage(1, a, b))
        else:
            if y2 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1+(3*n/2), y1+(3*n/2))), Border((x2, y2), (x2+(n/2), y2+(n/2))), (x1+(3*n/2), y1+(3*n/2)), (x2+(n/2), y2+(n/2)))
            else:
                return(_virage(1, a, b))
    else:
        if x < 0:
            if x1 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1-(3*n/2), y1-(3*n/2))), Border((x2, y2), (x2-(n/2), y2-(n/2))), (x1-(3*n/2), y1-(3*n/2)), (x2-(n/2), y2-(n/2)))
            else:
                return(_virage(0, a, b))
        if x > 0:
            if x1 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1+(3*n/2), y1+(3*n/2))), Border((x2, y2), (x2+(n/2), y2+(n/2))), (x1+(3*n/2), y1+(3*n/2)), (x2+(n/2), y2+(n/2)))
            else:
                return(_virage(0, a, b))
        if y < 0:
            if y1 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1+(3*n/2), y1-(3*n/2))), Border((x2, y2), (x2+(n/2), y2-(n/2))), (x2+(3*n/2), y2-(3*n/2)), (x2+(n/2), y2-(n/2)))
            else:
                return(_virage(0, a, b))
        else:
            if y1 > int(4*(taille/20)*sqrt(2)/2):
                return(Border((x1, y1), (x1-(3*n/2), y1+(3*n/2))), Border((x2, y2), (x2-(n/2), y2+(n/2))), (x1-(3*n/2), y1+(3*n/2)), (x2-(n/2), y2+(n/2)))
            else:
                return(_virage(0, a, b))


def circuit_creation(n: int) -> list:
    """
    Crée un circuit avec des bordures
    - n (int): nombre de _virages du circuit
    Retourne: liste de Border
    """
    x1, x2, y1, y2 = 20, 90, 20, 130
    circuit = []
    a, b = (x1, y1), (x2, y2)
    for _ in range(n):  # on enchaine ligne droite et _virage n fois
        n1 = randint(20, 80)
        l1, l2, a, b = _ligne_droite(n1, a, b)
        d = randint(0, 1)
        l3, l4, a, b = _virage(d, a, b)
        circuit += [l1, l2, l3, l4]
    return circuit
