"""
Fichier contenant les classes utilisées dans le programme

Il y a les voitures (:class:`Car`), les bordures du circuit (:class:`Border`), les réseaux
neuronaux (:class:`Network`) et les neurones eux-même (:class:`Neuron`).
"""


import math
import random
from math import exp
from typing import Optional, List
import time
import pygame
from pygame.math import Vector2 as Vector
from numpy import arccos, array, dot, pi, cross
from numpy.linalg import norm
import draw


def line_ray_intersection_point(ray_origin: (int, int), ray_direction: (int, int),
                                point1: (int, int), point2: (int, int)):
    """Donne le vecteur allant de l'origine vers le point d'intersection.

    Le "rayon" peut être assimilié à une demi-droite, dont on cherche à définir le point
    d'intersection avec un segment.
    Source du code : http://bit.ly/2VfSFOV

    Parameters
    ----------
    ray_origin: (:class:`int`, :class:`int`)
        Point d'origine du rayon à analyser
    ray_direction: (:class:`int`, :class:`int`)
        Direction du rayon, en coordonnées (x, y)
    point1: (:class:`int`, :class:`int`)
        Première extrémité du segment
    point2: (:class:`int`, :class:`int`)
        Deuxième extrémité du segment

    Returns
    -------
    (:class:`int`, :class:`int`):
        Coordonnées du point d'intersection, en x et y
    """
    # Convert to vectors
    ray_origin = Vector(ray_origin)
    ray_direction = Vector(ray_direction).normalize()
    point1 = Vector(point1)
    point2 = Vector(point2)

    # Ray-Line Segment Intersection Test in 2D
    # http://bit.ly/1CoxdrG
    v1 = ray_origin - point1
    v2 = point2 - point1
    v3 = Vector([-ray_direction[1], ray_direction[0]])
    try:
        t1 = v2.cross(v1) / v2.dot(v3)
        t2 = v1.dot(v3) / v2.dot(v3)
    except ZeroDivisionError:
        return []
    if t1 >= 0.0 and 0.0 <= t2 <= 1.0:
        temp = ray_origin + t1 * ray_direction
        return temp.x, temp.y
    return []


def line_intersection(line1, line2):
    """Donne le point d'intersection entre deux lignes

    Le "rayon" peut être assimilié à une demi-droite, dont on cherche à définir le point
    d'intersection avec un segment.

    Parameters
    ----------
    line1: Tuple[Tuple[:class:`int`]]
        Première ligne, constituée de deux points départ et arrivée, eux-même définis par des
        couples d'entiers
    line2: Tuple[Tuple[:class:`int`]]
        Deuxième ligne, constituée de deux points départ et arrivée, eux-même définis par des
        couples d'entiers

    Returns
    -------
    (:class:`int`, :class:`int`):
        Coordonnées du point d'intersection, en x et y
    """
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return []
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    if min(line1[0][0], line1[1][0]) <= x <= max(line1[0][0], line1[1][0]) and \
            min(line2[0][1], line2[1][1]) <= y < max(line2[0][1], line2[1][1]):
        return [x, y]
    return []


def sig(n: float, a=1):
    return (1/(1+exp(-a*n)))


class Border:
    """Représente une bordure de circuit

    Ligne droite allant de A(x,y) à B(x,y)
    """

    def __init__(self, A: tuple, B: tuple, color: pygame.Color):
        """Initialise la bordure

        Parameters
        ----------
        A: (:class:`int`, :class:`int`)
            Premier point de la ligne, en (x, y)
        B: (:class:`int`, :class:`int`)
            Deuxième point de la ligne, en (x, y)
        """
        assert isinstance(A, (tuple, list)) and isinstance(B, (tuple, list)) and len(
            A) == len(B) == 2, "A et B doivent être des tuples de longueur 2"
        self.color = color
        self.start = A
        self.end = B

    @property
    def points(self):
        """Tuple contenant le point de départ et le point d'arrivée de la ligne"""
        return (self.start, self.end)


class Car:
    """Représente une voiture

    Celle classe contient toutes les méthodes nécessaires à la création et la gestion de la voiture,
    pour la faire évoluer, récupérer les valeurs de son raytracing, et la remettre à zéro à la fin
    d'une évolution.
    """

    def __init__(self, circuit: List[Border], color: pygame.Color, abs_rotation: float = 0,
                 starting_pos: tuple = (80, 140)):
        """Initialise la voiture

        Parameters
        ----------
        circuit: List[Border]
            liste des bordures composant le circuit
        color:
            Couleur de la voiture [par défaut rouge]
        abs_rotation:
            Rotation par rapport au plan de la voiture [par défaut sud]
        starting_pos:
            Position de départ de la voiture en (x,y) [par défaut (80, 140)]
        """
        self.color: pygame.Color = color  #: Couleur de la voiture
        self.position: (int, int) = list(starting_pos)  #: Position actuelle
        self.init_pos: (int, int) = starting_pos  #: Position de départ
        self.init_rotation: float = abs_rotation  #: Rotation de départ
        self.abs_rotation: float = abs_rotation  #: Rotation actuelle
        #: Liste des bordures du circuit
        self.circuit: List[Border] = circuit[:-1]
        self.last_border: Border = circuit[-1]  #: Ligne d'arrivée du circuit
        self.start_time: float = time.time()  #: Timestamp de création de la voiture
        self.death_time: float = None  #: Timestamp de la mort de la voiture
        self.distance: float = 0  #: Distance parcourue depuis le début du circuit
        self.rays: List[int] = [-70, -50, -30, -10, 10,
                                30, 50, 70]  #: Angles des rayons (raytracing)
        self.rays_length: int = 80  #: Longueur des rayons du raytracing

    @property
    def distances(self) -> List[float]:
        """Retourne la distance de raytracing pour chaque rayon défini

        L'angle des rayons est défini à la création de la voiture, et est le même pour toutes les
        voitures.

        Returns
        -------
        List[:class:`float`]
            Distance de raytracing pour chaque angle défini"""
        return [self.raytrace(angle, self.rays_length, return_real_distance=True) for angle in self.rays]

    def reset(self):
        """Remet à zéro quelques options pour le prochain tour"""
        self.start_time = time.time()
        self.death_time = None
        self.distance = 0
        self.position = list(self.init_pos)
        self.abs_rotation = self.init_rotation

    def get_score(self):
        """Calcule le score de la voiture en fonction de la distance parcourue et du temps passé

        Returns
        -------
        :class:`int`:
            Score de la voiture à l'instant présent"""
        d = time.time() if self.death_time is None else self.death_time
        s = self.distance - (d-self.start_time)*5
        return round(s)

    def set_position(self, x: int, y: int):
        """Modifie la position absolue de la voiture

        Parameters
        ----------
        x:
            Nouvelle position de la voiture sur l'axe X (abscisse)
        y:
            Nouvelle position de la voiture sur l'axe Y (ordonnée)"""
        self.position = [x, y]

    def apply_vector(self, vector: Vector):
        """Applique un vecteur à la position de la voiture

        Parameters
        ----------
        vector:
            Vecteur à appliquer"""
        self.position[0] += vector.x
        self.position[1] += vector.y
        self.distance += vector.length()

    def raytrace(self, angle: int, max_distance: int = 100, use_absolute_angle: bool = False,
                 return_real_distance: bool = False):
        """Vérifie si le rayon d'angle donné rencontre un mur avant une certaine distance

        Parameters
        ----------
        angle:
            Angle du rayon en degrés, 0 étant l'avant de la voiture
        max_distance:
            Distance maximum à prendre en compte [par défaut 100]
        use_absolute_angle:
            Si l'angle donné est relatif au plan (1) ou à la voiture (0) [par défaut False]
        return_real_distance:
            Si la valeur retournée doit être la distance réelle, et non entre 0
            et 1 [par défaut False]

        Returns
        -------
        :class:`float`:
            Retourne la distance entre 0 et 'max', 0 étant une collision immédiate et 'max' à la
            distance maximum, ou -1 si aucune collision. La valeur de 'max' est définie par le
            paramètre `max_distance` si `return_real_distance = True`, 1 sinon."""
        assert all([isinstance(x, Border) for x in self.circuit]
                   ), "La liste du circuit ne doit contenir que des objets de type Border"
        if not use_absolute_angle:
            angle = self.abs_rotation + angle
        angle = math.radians(angle)
        # direction = vector(round(math.cos(angle), 5),
        #                    round(math.sin(angle), 5))
        ray_direction = Vector(2 * math.cos(angle), 2 * math.sin(angle))
        ray_direction.scale_to_length(max_distance)
        distances = []
        for line in self.circuit:
            distance1 = Vector(
                line.start[0]-self.position[0], line.start[1]-self.position[1]).length()
            distance2 = Vector(
                line.end[0]-self.position[0], line.end[1]-self.position[1]).length()
            if distance1 < max_distance or distance2 < max_distance:
                distances.append(line_ray_intersection_point(self.position, ray_direction,
                                                             line.start, line.end))
        distances = [Vector(x[0]-self.position[0], x[1]-self.position[1]).length()
                     for x in distances if len(x) != 0]
        if len(distances) == 0:
            return -1
        shortest_distance = min(distances)
        if shortest_distance > max_distance:
            return -1
        if return_real_distance:
            return shortest_distance
        return shortest_distance/max_distance

    def direction_vector(self) -> Vector:
        """Renvoie un vecteur unitaire dans la direction de self.abs_rotation"""
        return Vector(2 * math.cos(math.radians(self.abs_rotation)),
                      2 * math.sin(math.radians(self.abs_rotation)))

    def detection(self, screen: pygame.Surface, display_rays: Optional[str]) -> bool:
        """Détecte si la voiture est en collision avec une bordure du circuit

        Parameters
        ----------
        screen:
            La fenêtre du programme
        display_rays:
            Option d'affichage des rayons : sous forme de segment ('Ray'), de croix ('Cross'),
            ou aucun (None)
        """
        for i, a in enumerate(self.distances):
            if a != -1:
                if display_rays is not None:
                    draw.drawvec(screen, self, self.rays[i], a, display_rays)
            if 0 <= a <= 9:
                return 0
        return self.distance_to_segment(self.last_border) > 8

    def distance_to_segment(self, line: Border) -> float:
        """Retourne la distance la plus petite entre la voiture et un segment

        Parameters
        ----------
        line:
            Bordure définissant le segment à vérifier
        """
        P, A, B = array(self.position), array(line.start), array(line.end)
        if all(A == P) or all(B == P):
            return 0
        if arccos(dot((P - A) / norm(P - A), (B - A) / norm(B - A))) > pi / 2:
            return norm(P - A)
        if arccos(dot((P - B) / norm(P - B), (A - B) / norm(A - B))) > pi / 2:
            return norm(P - B)
        return round(norm(cross(A-B, A-P))/norm(B-A), 3)


class Network:
    """
    Représentation d'un réseau neuronal

    Le réseau est rattaché à une voiture, et utilise les données de cette voiture (raytracing) pour
    calculer la vitesse et la direction à prendre.

    Le but du programme étant d'obtenir un réseau neuronal le plus performant possible, ammenant sa
    voiture à la fin du circuit sans toucher aucune bordure.
    """

    def __init__(self, car: Car):
        """
        Initialise le réseau neuronal

        Chaque couche du réseau se voit attribué un nombre fixe de neurones, tous initialisés de
        manière aléatoire.

        Parameters
        ----------
        car:
            La voiture attribuée à ce réseau neuronal"""
        self.I_layer = [Neuron(6) for _ in range(len(car.rays)+2)]
        self.layer_2 = [Neuron(4) for _ in range(6)]
        self.layer_3 = [Neuron(2) for _ in range(4)]
        self.layer_4 = [Neuron(0) for _ in range(2)]
        self.score: int = 0  #: Score final du réseau
        self.dead: bool = False  #: Indique si la voiture est rentrée dans un mur
        self.car: Car = car  #: Voiture liée au réseau

    def update(self):
        """Recalcule les valeurs de chaque neurone à partir du raytracing de la voiture

        Le raytracing renvoie un certain nombre fixe de valeurs entre 0 et 1, correspondant à la
        distance du mur le plus proche vu par chaque angle. Deux autres neurones sont remplis avec
        la distance et l'angle actuel de la voiture, permettant un calcul semi récursif.
        """
        for i, n in enumerate(self.I_layer[:-2]):
            n.value = max(0, self.car.raytrace(
                self.car.rays[i], self.car.rays_length, return_real_distance=False))
        self.I_layer[-2].value = self.layer_4[0].value
        self.I_layer[-1].value = self.layer_4[1].value
        for i, neuron in enumerate(self.layer_2):
            neuron.update_value(self.I_layer, i)
        for i, neuron in enumerate(self.layer_3):
            neuron.update_value(self.layer_2, i)
        for i, neuron in enumerate(self.layer_4):
            neuron.update_value(self.layer_3, i)

    @property
    def direction(self) -> float:  # between -2 and 2
        """Direction de la voiture, entre -2.0 et 2.0"""
        return round(self.layer_4[0].value*4-2, 3)

    @property
    def engine(self) -> float:  # between 0.2 and 1
        """Vitesse de la voiture, entre 0.2 et 1"""
        return min(1, (self.layer_4[1].value*1.2)+0.2)

    def from_json(self, data: dict):
        """Recrée le réseau et tous ses neurones à partir de données préalablement enregistrées

        Parameters
        ----------
        data:
            Données enregistrées sur le réseau neuronal
        """
        if data is None:
            return
        self.I_layer = [Neuron(0) for _ in range(data["layers"][0])]
        self.layer_2 = [Neuron(0) for _ in range(data["layers"][1])]
        self.layer_3 = [Neuron(0) for _ in range(data["layers"][2])]
        self.layer_4 = [Neuron(0) for _ in range(data["layers"][3])]
        for e, n in enumerate(data["neurons"][0]):
            self.I_layer[e].from_json(n)
        for e, n in enumerate(data["neurons"][1]):
            self.layer_2[e].from_json(n)
        for e, n in enumerate(data["neurons"][2]):
            self.layer_3[e].from_json(n)
        for e, n in enumerate(data["neurons"][3]):
            self.layer_4[e].from_json(n)


class Neuron:
    """
    Neurone composant le réseau neuronal (:class:`Network`)

    Il possède une valeur, une constante, et une liste de poids régulant l'influence de ce neurone
    sur la couche suivante.
    """

    def __init__(self, weigth_len: int):
        """Initialise le neurone

        La valeur est fixée à 0, la liste des poids est tirée aléatoirement entre -2.0 et 2.0 pour
        chaque poids, et la constante est aléatoire entre -1.0 et 1.0.

        Parameters
        ----------
        weigth_len:
            Nombre de poids de la couche suivante
        """
        self.value: float = 0  #: Valeur actuelle du neurone
        self.weight = [random.random()*4-2 for i in range(weigth_len)]
        self.bias: float = random.random()*2-1  #: Constante du neurone

    def normalize(self):
        """Normalise la valeur actuelle du neurone pour s'assurer qu'elle soit entre 0 et 1

        On utilise ici la fonction sigmoide pour plus de modularité, avec un coefficient de 3."""
        self.value = sig(self.value, 3)

    def update_value(self, neurons: List['Neuron'], target):
        """Recalcule la valeur du neurone à partir des neurones de la couche précédente

        La valeur est calculée en faisant la somme coefficientée de la valeur des autres neurones,
        puis en y ajoutant la constante de ce neurone.
        Pour finir, on passe par une normalisation de la valeur afin de la rendre utilisable.

        Parameters
        ----------
        neurons:
            Liste des neurones de la couche précédente
        target:
            Indice du neurone actuel, utilisé pour retrouver les bons poids dans la liste des poids
            des précédents neurones
        """
        self.value = sum([x.value*x.weight[target]
                          for x in neurons]) + self.bias
        self.normalize()

    def from_json(self, data: dict):
        """Recrée le neurone à partir de données préalablement enregistrées

        Parameters
        ----------
        data:
            Données enregistrées sur le neurone
        """
        self.value = data["value"]
        self.weight = data["weight"]
        self.bias = data["bias"]

    def __str__(self):
        return str((self.value, self.weight, self.bias))

    def __repr__(self):
        return str(self.value)
