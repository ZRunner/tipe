"""
Fichier contenant différentes méthodes relative à l'affichage de donnés dans la fenêtre.
"""

import pygame
import time
from math import radians, cos, sin, ceil
from typing import List
from config_manager import Config, load_from_filename
from classes import Border, Car, Network

Vector = pygame.math.Vector2
SETTINGS: Config = None


def init():
    global SETTINGS
    SETTINGS = load_from_filename("settings.yaml")


def circuit(screen: pygame.Surface, circuit: List[Border]):
    """Création du circuit sur l'écran

    Parameters
    ----------
    screen:
        La fenêtre du programme
    circuit:
        Liste de toutes les bordures
    """
    for i in circuit:
        pygame.draw.line(screen, i.color, i.start,
                         i.end, ceil(SETTINGS.scale_avg))


def rotate(car: Car, X: (int, int)) -> list:
    """Applique une rotation à un point selon la position et la rotation de la voiture

    Parameters
    ----------
    car:
        Voiture de référence
    X:
        Position du point

    Returns
    -------
    list:
        Nouveau point
    """
    x = (X[0]-car.position[0])*cos(radians(car.abs_rotation)) - \
        (X[1]-car.position[1])*sin(radians(car.abs_rotation))
    y = (X[1]-car.position[1])*cos(radians(car.abs_rotation)) + \
        (X[0]-car.position[0])*sin(radians(car.abs_rotation))
    return [x + car.position[0], y + car.position[1]]


def car(screen: pygame.Surface, cars: List[Car]):
    """Dessine les voitures sur le circuit

    Parameters
    ----------
    screen:
        La fenêtre du programme
    cars:
        Liste de toutes les voitures (type Car)
    """
    car_length = ceil(10 * SETTINGS.scale_avg)
    car_width = ceil(7 * SETTINGS.scale_avg)
    line_w = ceil(2 * SETTINGS.scale_avg)
    for car in cars:
        if not isinstance(car.color, pygame.Color):
            car.color = pygame.Color(car.color)
        A = rotate(car, [car.position[0] - car_length,
                         car.position[1] - car_width])
        B = rotate(car, [car.position[0] + car_length,
                         car.position[1] - car_width])
        C = rotate(car, [car.position[0] + car_length,
                         car.position[1] + car_width])
        D = rotate(car, [car.position[0] - car_length,
                         car.position[1] + car_width])
        pygame.draw.line(screen, car.color, A, B, line_w)
        pygame.draw.line(screen, car.color, B, C, line_w)
        pygame.draw.line(screen, car.color, C, D, line_w)
        pygame.draw.line(screen, car.color, D, A, line_w)


def drawvec(screen: pygame.Surface, car: Car, angle: int, length: int, style: str):
    """Dessine un rayon partant d'une voiture
    Ce rayon est défini par la position de la voiture ainsi que l'angle et la longueur donnée

    Parameters
    ----------
    screen:
        La fenêtre du programme
    car:
        La voiture propriétaire de ce rayon
    angle:
        L'angle du rayon, en degrés
    length:
        La longueur du rayon
    style:
        Le style a utiliser (une croix au bout, ou un trait droit)
    """
    if style not in ["Ray", "Cross"]:
        return
    v = Vector(2 * cos(radians(car.abs_rotation + angle)),
               2 * sin(radians(car.abs_rotation + angle)))
    v.scale_to_length(length)
    new_pos = (car.position[0]+v.x, car.position[1]+v.y)
    if style == "Ray":
        pygame.draw.line(screen, car.color, car.position, new_pos, 1)
    elif style == "Cross":
        size = ceil(5 * SETTINGS.scale_avg/2)
        a = new_pos[0]-size, new_pos[1]-size
        b = new_pos[0]+size, new_pos[1]+size
        c = new_pos[0]-size, new_pos[1]+size
        d = new_pos[0]+size, new_pos[1]-size
        pygame.draw.line(screen, car.color, a, b, 1)
        pygame.draw.line(screen, car.color, c, d, 1)


def general_stats(screen: pygame.Surface, font: pygame.font, clock: pygame.time.Clock, gen_nbr: int,
                  cars_nbr: int, start_time: float):
    """Affiche les informations générales à l'écran

    Ces informations sont constituées des FPS actuels, du numéro de génération, du nombre de
    voitures restantes, et du temps passé depuis le début de la génération.

    Parameters
    ----------
    screen:
        La fenêtre du programme
    font: :mod:`pygame.font`
        La police à utiliser
    clock:
        L'horloge interne de Pygame
    gen_nbr:
        Le numéro de génération
    cars_nbr:
        Le nombre de voitures restantes
    start_time:
        Timestamp du début de la génération
    """
    texts = list()
    bg = SETTINGS.colors['background']
    text_color = SETTINGS.colors['text']
    # FPS
    t = clock.get_rawtime()
    nbr = 0 if t == 0 else round(1000/t)
    if nbr < 7:
        # color = (255, 0, 0)
        color = SETTINGS.colors['fps-colors'][0]
    elif nbr < 12:
        # color = (255, 153, 0)
        color = SETTINGS.colors['fps-colors'][1]
    else:
        # color = (51, 102, 0)
        color = SETTINGS.colors['fps-colors'][2]
    fps = font.render("FPS: "+str(nbr), True, color, bg)
    texts.append(fps)
    # Generation Nbr
    if gen_nbr is not None:
        generations = font.render(
            "Génération "+str(gen_nbr), True, text_color, bg)
        texts.append(generations)
    # Alive networks
    if cars_nbr is not None:
        s = "s" if cars_nbr > 1 else ""
        cars = font.render("{0} voiture{1} restante{1}".format(
            cars_nbr, s), True, text_color, bg)
        texts.append(cars)
    # Elapsed time
    t = round(time.time()-start_time, 2)
    elapsed_time = font.render("Temps : "+str(t), True, text_color, bg)
    texts.append(elapsed_time)
    # Display them all
    x = ceil(10 * SETTINGS.scale_x)
    y = ceil(5 * SETTINGS.scale_y)
    for e, t in enumerate(texts):
        screen.blit(t, (x, y + ceil(e*15*SETTINGS.scale_y)))


def car_specs(screen: pygame.Surface, font: pygame.font, network: Network):
    """Affiche des informations sur la voiture sélectionnée

    Ces informations contionnent le score actuel de la voiture, sa direction et sa vitesse

    Parameters
    ----------
    screen:
        La fenêtre du programme
    font: :mod:`pygame.font`
        La police utilisée
    network:
        Le réseau neuronal dont les informations seront extraites
    """
    direction = round(network.direction, 3)
    engine = round(network.engine, 3)
    color = SETTINGS.colors["dead-stats"] if network.dead else SETTINGS.colors["text"]
    bg = SETTINGS.colors["background"]
    _, y = SETTINGS.screen_size
    x = ceil(7 * SETTINGS.scale_x)
    # Score
    score = network.car.get_score()
    text3 = font.render(f"Score: {score}", True, color, bg)
    y2 = y - ceil(50*SETTINGS.scale_y)
    screen.blit(text3, (x, y2))
    # Direction
    y2 = y - ceil(35*SETTINGS.scale_y)
    text1 = font.render(f"Direction: {direction}", True, color, bg)
    screen.blit(text1, (x, y2))
    # Vitesse
    y2 = y - ceil(20*SETTINGS.scale_y)
    text2 = font.render(f"Engine: {engine}", True, color, bg)
    screen.blit(text2, (x, y2))


def car_network(screen: pygame.Surface, font: pygame.font, network: Network):
    """Affiche le réseau neuronal d'une voiture

    Chaque neurone sera représenté avec sa valeur, ainsi que les liaisons pondérées entre eux

    Parameters
    ----------
    screen:
        La fenêtre du programme
    font: :mod:`pygame.font`
        La police utilisée
    network:
        Le réseau neuronal dont les informations seront extraites
    """
    _, y = SETTINGS.screen_size
    x = ceil(25 * SETTINGS.scale_x)
    diam = 15
    y -= ceil((20+(diam+10)*len(network.I_layer)) * SETTINGS.scale_y)
    diam = ceil(diam * SETTINGS.scale_avg)
    circle_color = SETTINGS.colors["neuron-color"]
    text_color = SETTINGS.colors["neuron-text-color"]
    circles = list()
    texts = list()
    neurons = list()
    y_space = ceil(20 * SETTINGS.scale_y)
    x_space = ceil(80 * SETTINGS.scale_x)
    for layer in [network.I_layer, network.layer_2, network.layer_3, network.layer_4]:
        height = (diam+y_space)*len(layer)
        y2 = y + height/2
        temp = list()
        for n in layer:
            circles.append((screen, circle_color, (x, round(y2)), diam))
            texts.append(
                (font.render(str(round(n.value*1000)), True, text_color, None), (x, y2)))
            temp.append((n, (x, y2)))
            y2 -= diam + y_space
        neurons.append(temp)
        x += diam + x_space
    for e in range(len(neurons)-1):
        for n1 in neurons[e]:
            for e2, n2 in enumerate(neurons[e+1]):
                n_weight = (n1[0].weight[e2]+2)/4
                color = (round(n_weight*200),)*3
                w = ceil((round(n_weight*3)+1) * SETTINGS.scale_avg)
                pygame.draw.line(screen, color, n1[1], n2[1], w)
    for c in circles:
        pygame.draw.circle(*c)
    for text, coo in texts:
        rect = text.get_rect()
        screen.blit(text, (coo[0]-rect.width/2, coo[1]-rect.height/2))


def pause_screen(screen: pygame.Surface, font: pygame.font):
    """Obscurcis l'écran pour indiquer à l'utilisateur que le programme est en pause

    Parameters
    ----------
    screen:
        La fenêtre du programme
    font: :mod:`pygame.font`
        La police à utiliser
    """
    color = (10, 10, 10)
    purple_image = pygame.Surface(SETTINGS.screen_size)
    purple_image.set_colorkey((0, 0, 0))
    purple_image.set_alpha(150)
    pygame.draw.rect(purple_image, color, purple_image.get_rect(), 0)
    screen.blit(purple_image, (0, 0))
    x = SETTINGS.screen_size[0]/2
    y = SETTINGS.screen_size[1]*0.1
    text1 = font.render("Programme en pause", True, (255, 255, 255), None)
    text2 = font.render("Appuyez sur P pour relancer",
                        True, (255, 255, 255), None)
    rect1 = text1.get_rect()
    rect2 = text2.get_rect()
    screen.blit(text1, (x-rect1.width/2, y-rect1.height/2))
    screen.blit(text2, (x-rect2.width/2, y+(rect1.height*1.2)-rect2.height/2))
