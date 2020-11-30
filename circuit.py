"""
Fichier contenant le nécessaire pour générer un circuit

Le circuit est généré de manière procédurale, à partir de quelques points de référence.
Des lignes sont tracées entre ces points, puis chaque ligne est pliée plusieurs fois de suite
jusqu'à obtenir le tracé général du circuit. Une épaisseur pseudo-aléatoire est ensuite ajoutée.

La seule classe publique est ici :func:`circuit_creation`.

Les constantes affichées ici sont exprimées en pixels selon la taille par défaut de la fenêtre,
mais sont adaptées à la taille réelle.
"""

import typing
import random
from math import hypot, sqrt, degrees, atan2
import pygame
from pygame.math import Vector2 as Vector
from classes import Border
from config_manager import Config

#: Point approximatif de départ du circuit
START_POINT = (50, 120)
#: Point approximatif d'arrivée du circuit
END_POINT = (1100, 100)
#: Liste de points utilisés pour dessiner la courbe générale
INTERMEDIATE_POINTS = [(500, 160), (650, 600), (900, 600)]
#: Mesure minimum d'un angle pour le considérer valide, en degrés
MIN_ANGLE_DEGREES = 90
#: Mesure maximum d'un angle pour le considérer valide, en degrés
MAX_ANGLE_DEGREES = 175
#: Longueur minimale d'un segment
MIN_SEGMENT_LENGTH = 40
#: Coefficient du coût maximal d'un nouveau point (calculé à partir de la distance à son segment
#: d'origine)
MAX_COST_COEF = 1.0
#: Amplitude de la distance entre un nouveau point et son segment d'origine, entre 0 et 1
RANDOM_GENPOINT_AMPLITUDE = 0.2
#: Largeur minimale du circuit
MIN_PATH_WIDTH = 70
#: Largeur maximale du circuit
MAX_PATH_WIDTH = 105
#: Nombre de générations successives à appliquer sur la courbe. Plus ce nombre est grand, plus la
#: courbe sera détaillée
GENERATIONS_NUMBER = 9


def calc_angle(point_a: tuple, point_b: tuple, point_c: tuple) -> float:
    """Calcule un angle ABC à partir de coordonnées

    Parameters
    ----------
    point_a: (:class:`int`, :class:`int`)
        Premier point de l'angle, sous forme (x, y)
    point_b: (:class:`int`, :class:`int`)
        Deuxième point de l'angle, sous forme (x, y)
    point_c: (:class:`int`, :class:`int`)
        Troisième point de l'angle, sous forme (x, y)

    Returns
    -------
    :class:`float`:
        Mesure de l'angle, en degrés
    """
    angle = degrees(atan2(point_c[1]-point_b[1], point_c[0]-point_b[0]) -
                    atan2(point_a[1]-point_b[1], point_a[0]-point_b[0]))
    return angle-360 if angle > 180 else (360+angle if angle < -180 else angle)


def calc_distance(point_a: tuple, point_b: tuple) -> int:
    """Calcule la distance entre deux points A et B, assimilé à la longueur du segment [A, B]

    Parameters
    ----------
    point_a: (:class:`int`, :class:`int`)
        Premier point du segment, sous forme (x, y)
    point_b: (:class:`int`, :class:`int`)
        Deuxième point du segment, sous forme (x, y)

    Returns
    -------
    :class:`int`:
        Longueur du segment, arrondi à l'entier le plus proche
    """
    return round(hypot(point_a[0]-point_b[0], point_a[1]-point_b[1]))


def generate_point(point_a: tuple, point_b: tuple, screen_size: tuple, last_move: tuple,
                   i: int = 0) -> ((int, int), (int, int)):
    """Génère un point entre deux autres

    Parameters
    ----------
    point_a: (:class:`int`, :class:`int`)
        Premier point du segment à plier, en (x, y)
    point_b: (:class:`int`, :class:`int`)
        Deuxième point du segment à plier, en (x, y)
    screen_size: (:class:`int`, :class:`int`)
        Taille de la fenêtre, en (x, y)
    last_move: (:class:`int`, :class:`int`)
        Dernier mouvement, en (dx, dy) : chaque coordonnée prend 1 si le delta était positif,
        -1 sinon. Permet de garder une consistance dans les virages
    i:
        Nombre de tentatives échouées pour ce point

    Returns
    -------
    ((:class:`int`, :class:`int`), (:class:`int`, :class:`int`)):
        Coordonnées du nouveau point, et mouvement effectué (équivalent du last_move)
    """
    i += 1
    cost = 1
    max_cost = 0
    angle = 0
    middle = [0, 0]
    middle[0] = (point_a[0]+point_b[0])//2
    middle[1] = (point_a[1]+point_b[1])//2
    min_angle = MIN_ANGLE_DEGREES
    # ---
    radius_max = max(abs(point_a[0] - point_b[0]),
                     abs(point_a[1] - point_b[1]))
    last_move[0] = last_move[0] if random.random() < 0.7 else (
        1 if random.random() < 0.5 else -1)
    new_x = middle[0] + round(radius_max * random.uniform(0.001,
                                                          RANDOM_GENPOINT_AMPLITUDE) * last_move[0])
    last_move[1] = last_move[1] if random.random() < 0.7 else (
        1 if random.random() < 0.5 else -1)
    new_y = middle[1] + round(radius_max * random.uniform(0.001,
                                                          RANDOM_GENPOINT_AMPLITUDE) * last_move[1])
    # ---
    if i >= 700:
        return (new_x, new_y), last_move
    check_borders = MAX_PATH_WIDTH < new_x < screen_size[0]-MAX_PATH_WIDTH \
        and MAX_PATH_WIDTH < new_y < screen_size[1]-MAX_PATH_WIDTH
    if check_borders:
        distance_a_b = calc_distance(point_a, point_b)
        cost = round(distance_a_b
                     + calc_distance(point_b, (new_x, new_y))
                     - calc_distance(point_a, (new_x, new_y)))
        max_cost = round(distance_a_b * MAX_COST_COEF)
        if cost < max_cost:
            angle = abs(calc_angle(point_a, (new_x, new_y), point_b))
            min_angle += 250/sqrt(distance_a_b)
    if cost > max_cost or not check_borders or angle < MIN_ANGLE_DEGREES or \
            angle > MAX_ANGLE_DEGREES:
        (new_x, new_y), last_move = generate_point(
            point_a, point_b, screen_size, last_move, i)
    return (round(new_x), round(new_y)), last_move


def check_angles(pathway: typing.List[tuple]) -> bool:
    """Vérifie si le chemin ne contient pas d'angle bizarre

    Chaque angle bizarre sera supprimé, pour "nettoyer" la courbe.

    Un angle est considéré "bizarre" s'il est trop plat ou trop aigu, en référence aux deux
    constantes 'MIN_ANGLE_DEGREES' et 'MAX_ANGLE_DEGREES'.

    Parameters
    ----------
    pathway:
        Liste de tous les points composant le chemin

    Returns
    -------
    :class:`bool`:
        True si au moins un point a été supprimé
    """
    if len(pathway) < 3:
        return True
    result = True
    wrong_indexes = list()
    for index in range(1, len(pathway)-1):
        angle = abs(
            round(calc_angle(pathway[index-1], pathway[index], pathway[index+1])))
        if angle > 180:
            angle = 360-angle
        result = MIN_ANGLE_DEGREES < angle < MAX_ANGLE_DEGREES
        if not result:
            wrong_indexes.insert(0, index)
    for i in wrong_indexes:
        pathway.pop(i)
    if len(wrong_indexes) > 0:
        check_angles(pathway)
        return True
    return False


def add_width(pathway: typing.List[tuple], colors: typing.Dict[str, pygame.Color],
              screen_size: typing.Tuple[int]) -> dict:
    """Elargit le circuit à partir du tracé de base

    Pour chaque segment du tracé, on calcule la médiatrice du segment puis on trouve deux points
    sur cette médiatrice dont la distance respecte les constantes posées. Un nettoyage est ensuite
    réalisé pour supprimer les angles trop bruts ou inutiles, par la fonction :func:`check_angles`.

    Parameters
    ----------
    pathway:
        Liste des points du tracé de base
    colors:
        Dictionnaire des couleurs à utiliser
    screen_size: (:class:`int`, :class:`int`)
        Taille en X,Y de la fenêtre

    Returns
    -------
    :class:`dict`:
        Dictionnaire contenant le premier point supérieur ('point1'), le premier point inférieur
        ('point2') et toutes les :class:`classes.Border` du circuit ('bordures')
    """
    points_over = list()
    points_under = list()
    result = list()
    delta = -round(MIN_PATH_WIDTH/12), round(MIN_PATH_WIDTH/12)
    new_delta = min(MIN_PATH_WIDTH + random.randrange(*delta), MAX_PATH_WIDTH)
    # First point
    vect = Vector(pathway[1][0]-pathway[0][0], pathway[1][1]-pathway[0][1])
    vect.rotate_ip(90)
    vect.scale_to_length(new_delta)
    points_over.append((pathway[0][0] - vect.x/2, pathway[0][1] - vect.y/2))
    points_under.append((pathway[0][0] + vect.x/2, pathway[0][1] + vect.y/2))
    # Other points
    for enum in range(1, len(pathway)-1):
        point1, point2, point3 = pathway[enum -
                                         1], pathway[enum], pathway[enum+1]
        vect = Vector(point2[0]-point1[0], point2[1]-point1[1]) \
            + Vector(point3[0]-point2[0], point3[1]-point2[1])
        vect.rotate_ip(90)
        new_delta = max(min(new_delta + random.randrange(*delta),
                            MAX_PATH_WIDTH), MIN_PATH_WIDTH)
        vect.scale_to_length(new_delta)
        # points_over.append(point2)
        points_over.append((point2[0]-vect.x/2, point2[1]-vect.y/2))
        points_under.append((point2[0]+vect.x/2, point2[1]+vect.y/2))
    # Last point
    vect = Vector(pathway[-1][0]-pathway[-2][0], pathway[-1][1]-pathway[-2][1])
    vect.rotate_ip(90)
    vect.scale_to_length(new_delta)
    points_over.append((pathway[-1][0] - vect.x/2, pathway[-1][1] - vect.y/2))
    points_under.append((pathway[-1][0] + vect.x/2, pathway[-1][1] + vect.y/2))
    # Cleanup of points
    check_angles(points_over)
    check_angles(points_under)
    for path in (points_over, points_under):
        for index in range(len(path)-1):
            if colors is None:  # debug only - couleur aléatoire
                color = ((index*100+70) % 255, (index*90+20) % 255, (index*50+40) % 255)
            else:
                color = colors["borders"]
            if path[index][1] > screen_size[1] - 10:
                path[index][1] = screen_size[1] - 10
            elif path[index][1] < 10:
                path[index][1] = 10
            result.append(Border(path[index], path[index+1], color))
    black = (10, 10, 10)
    result.append(
        Border(points_over[0], points_under[0], colors["border-begin"] if colors is not None else black))
    result.append(
        Border(points_over[-1], points_under[-1], colors["border-end"] if colors is not None else black))
    return {"bordures": result, "point1": points_under[0], "point2": points_over[0]}


def fix_points(scale_x: float, scale_y: float):
    """Recalcule toutes les constantes en appliquant l'échelle donnée par la configuration

    Parameters
    ----------
    scale_x:
        Echelle en x
    scale_y:
        Echelle en y
    """
    global START_POINT, END_POINT, INTERMEDIATE_POINTS, MIN_SEGMENT_LENGTH
    global MIN_PATH_WIDTH, MAX_PATH_WIDTH
    coef_g = (scale_x+scale_y)/2

    def update_pt(pt: (int, int)) -> (int, int):
        return pt[0]*scale_x, pt[1]*scale_y
    START_POINT = update_pt(START_POINT)
    END_POINT = update_pt(END_POINT)
    INTERMEDIATE_POINTS = [update_pt(x) for x in INTERMEDIATE_POINTS]
    MIN_SEGMENT_LENGTH = coef_g * MIN_SEGMENT_LENGTH
    MIN_PATH_WIDTH = coef_g * MIN_PATH_WIDTH
    MAX_PATH_WIDTH = coef_g * MAX_PATH_WIDTH


def circuit_creation(settings: Config) -> dict:
    """Fonction principale générant le circuit.

    C'est elle qui appelle toutes les autres fonctions dans le bon ordre et retourne un circuit
    complet.

    Parameters
    ----------
    settings:
        Paramètres du programme, notamment pour l'échelle et les couleurs

    Returns
    -------
    :class:`dict`:
        Dictionnaire contenant le premier point supérieur ('point1'), le premier point inférieur
        ('point2') et toutes les :class:`classes.Border` du circuit ('bordures')
    """
    fix_points(settings.scale_x, settings.scale_y)
    pathway = [START_POINT] + INTERMEDIATE_POINTS + [END_POINT]
    for _ in range(GENERATIONS_NUMBER):
        index2 = 0
        last_move = [-1, 1]
        for _ in range(len(pathway)-1):
            if calc_distance(pathway[index2], pathway[index2+1]) > MIN_SEGMENT_LENGTH:
                line = pathway[index2], pathway[index2+1]
                new_point, last_move = generate_point(
                    *line, settings.screen_size, last_move)
                pathway.insert(index2+1, new_point)
                index2 += 1
            index2 += 1
    return add_width(pathway, settings.colors, settings.screen_size)
