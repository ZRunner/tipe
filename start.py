"""
Fichier principal du programme.

C'est celui à utiliser pour lancer le programme, qui importera tous les autres fichiers
automatiquement.

Utilisation : `python start.py`
"""

import time
import cProfile
import pstats
import io
import typing
import copy
from pstats import SortKey
from math import ceil
import pygame
import draw
from circuit import circuit_creation
from classes import Car, Border, Network
from config_manager import Config, load_from_filename
from evolve import darwin
from backup_manager import BackupManager


Vector = pygame.math.Vector2
SETTINGS: Config = None
FPS = 20  # Sert à approximativement limiter les fps, sans avoir beaucoup d'impact sur les fps réels


def calc_starting_pos(point_a, point_b) -> ((int, int), float):
    """
    Calcule la position de départ des voitures, en fonction du circuit

    Parameters
    ----------
    point_a: (:class:`int`, :class:`int`)
        Premier point de la bordure supérieure du circuit
    point_b: (:class:`int`, :class:`int`)
        Premier point de la bordure inférieure du circuit

    Returns
    -------
    ((:class:`int`, :class:`int`), :class:`float`)
        Les coordonnées du point de départ, et la rotation adéquate
    """
    vect = Vector(point_a[0]-point_b[0], point_a[1]-point_b[1])
    vect.scale_to_length(vect.length()/2)
    new_point = point_b[0]+vect.x, point_b[1]+vect.y
    n = Vector(0, 1)
    new_angle = -round(vect.angle_to(n))
    vect = vect.rotate(-90)
    vect.scale_to_length(20)
    new_point = round(new_point[0]+vect.x), round(new_point[1]+vect.y)
    return new_point, new_angle


def check_events() -> int:
    """Vérifie les touches entrées par l'utilisateur

    Returns
    -------
    int:
        0 si rien ne se passe, 1 si la génération doit recommencer, 2 si le programme doit se
        quitter, 3 si le programme doit se mettre en pause
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return 2
        if event.type == pygame.KEYDOWN:
            if event.unicode == "r":  # reset:
                return 1
            if event.unicode == 'p':  # pause
                return 3
    return 0


def manual_loop(screen: pygame.Surface, circuit: typing.List[Border]):
    """
    Boucle principale pour le mode manuel du programme

    Parameters
    ----------
    screen:
        La fenêtre du programme
    circuit:
        La liste des bordures représentant le circuit
    """
    screen_width = SETTINGS.screen_size[0]
    clock = pygame.time.Clock()
    small_font = pygame.font.SysFont('Arial', ceil(18*SETTINGS.scale_avg))
    title_font = pygame.font.SysFont('Arial', ceil(30*SETTINGS.scale_avg))
    dt = 1
    color = pygame.Color(SETTINGS.car_color)
    init_pos, init_angle = calc_starting_pos(
        circuit["point1"], circuit["point2"])
    car = Car(circuit["bordures"], color=color,
              starting_pos=init_pos, abs_rotation=init_angle)
    running = True
    start_time = time.time()

    on_pause = False

    while running:
        temp = check_events()
        if temp == 2:
            break
        if temp == 3:
            on_pause = not on_pause

        screen.fill(SETTINGS.colors["background"])
        draw.circuit(screen, circuit["bordures"])
        draw.car(screen, [car])
        delta = dt * FPS / 1000

        if not on_pause:
            pressed = pygame.key.get_pressed()
            if pressed[SETTINGS.left_key]:
                car.abs_rotation -= SETTINGS.car_maniability * delta
            if pressed[SETTINGS.right_key]:
                car.abs_rotation += SETTINGS.car_maniability * delta
            car.apply_vector(car.direction_vector())

            if min(car.position) < 0:
                car.set_position(max(car.position[0], 0), max(car.position[1], 0))
            if max(car.position) > screen_width:
                car.set_position(min(car.position[0], screen_width), min(
                    car.position[1], screen_width))
            if not car.detection(screen, SETTINGS.display_rays):
                running = False
                print("Votre voiture a touché un mur - fin de la partie")

        draw.general_stats(screen, small_font, clock, None, None, start_time)
        if on_pause:
            draw.pause_screen(screen, title_font)
            start_time += dt/1000
        pygame.display.flip()
        dt = clock.tick(FPS)

    for _ in range(30):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        time.sleep(0.05)


def AI_loop(screen: pygame.Surface, circuit: dict) -> Network:
    """
    Boucle principale pour le mode automatique du programme

    Le but ici est d'entraîner des IA pour qu'elles soient le plus performant possible sur le
    circuit, donc en trouver au moins une qui arrive à la fin du circuit sans toucher aucune
    bordure.

    Parameters
    ----------
    screen:
        La fenêtre du programme
    circuit:
        Un dictionnaire contenant la liste des bordures représentant le circuit, ainsi que les deux
        points définissant la ligne de départ

    Returns
    -------
    Network:
        Le meilleur réseau de la dernière génération complétée
    """
    print("Astuce : Appuyez sur la touche R si une voiture tourne en rond\n")
    clock = pygame.time.Clock()
    small_font = pygame.font.SysFont('Arial', ceil(18*SETTINGS.scale_avg))
    title_font = pygame.font.SysFont('Arial', ceil(30*SETTINGS.scale_avg))
    dt = 1
    init_pos, init_angle = calc_starting_pos(
        circuit["point1"], circuit["point2"])
    cars = [Car(circuit["bordures"], color=SETTINGS.colors["cars"], starting_pos=init_pos,
                abs_rotation=init_angle) for _ in range(SETTINGS.cars_number)]
    networks = [Network(c) for c in cars]
    networks[0].from_json(BackupManager().load()["network"])
    networks[0].car.color = "#00FF00"
    running = True

    increment = 0
    last_sorted_networks = None
    on_pause = False

    while running:
        increment += 1
        endgen = False
        cleanup_done = False
        start_time = time.time()
        while not endgen:

            temp = check_events()
            if temp == 1:
                endgen = True
            if temp == 2:
                return last_sorted_networks[0] if last_sorted_networks is not None else None
            if temp == 3:
                on_pause = not on_pause

            screen.fill(SETTINGS.colors["background"])
            draw.circuit(screen, circuit["bordures"])
            draw.car(screen, (net.car for net in networks))

            delta = dt * FPS / 1000
            if not on_pause:
                # Gestion du mouvement de la voiture
                for net in networks:
                    if not net.dead:
                        net.update()
                        net.car.abs_rotation += SETTINGS.car_maniability * delta * net.direction

                        net.car.apply_vector(
                            net.car.direction_vector() * net.engine * 2 * SETTINGS.scale_avg)
                        if not net.car.detection(screen, SETTINGS.display_rays):
                            net.dead = True
                            net.car.death_time = time.time()

                survived = sum(1 for n in networks if not n.dead)
                if survived == 0:
                    endgen = True
                elif time.time()-start_time > 10 and not cleanup_done:
                    for net in networks:
                        if (not net.dead) and net.car.position[0] < 150:
                            net.dead = True
                            net.car.death_time = time.time()

            draw.general_stats(screen, small_font, clock,
                               increment, survived, start_time)
            draw.car_specs(screen, small_font, networks[0])
            draw.car_network(screen, small_font, networks[0])
            if on_pause:
                draw.pause_screen(screen, title_font)
                elapsed = dt/1000
                start_time += elapsed
                for net in networks:
                    if not net.dead:
                        net.car.start_time += elapsed
            pygame.display.flip()
            dt = clock.tick(FPS)

        arrival = circuit["bordures"][-1]  # ligne d'arrivée
        # calcul des scores
        for net in networks:
            net.score = net.car.get_score()
            if net.car.distance_to_segment(arrival) <= 8:
                net.score += 300  # points bonus si la voiture a atteint la ligne d'arrivée
        average = round(sum([net.score for net in networks])/len(networks))
        print(f"Génération N°{increment} terminée - score moyen : {average}")
        last_sorted_networks = copy.deepcopy(networks)

        # Darwin
        networks = darwin(networks)

        # Reset des réseaux/voitures
        for net in networks:
            net.dead = 0
            # net.car.position = [80, 130]
            net.car.color = SETTINGS.colors["cars"]
            net.car.reset()
        networks[0].car.color = SETTINGS.colors["main_car"]


def main():
    """
    Fonction principale, lançant tout le programme selon la configuration donnée.

    La configuration du programme est disponible dans le fichier `settings.yaml`.
    """
    print("""Lancement du programme

    Assurez-vous que toutes les dépendances utilisées soient installées sur votre ordinateur ;
    si besoin entrez `pip install -r requirements.txt` dans votre console
    """)

    # Chargement de la configuration
    global SETTINGS
    try:
        SETTINGS = load_from_filename("settings.yaml")
    except AssertionError as e:
        print("Erreur lors du chargement de la configuration :\n"+e.args[0])
        return

    # Démarrage du debug
    if SETTINGS.debug_mode:
        pr = cProfile.Profile()
        pr.enable()

    draw.init()
    pygame.init()
    screen = pygame.display.set_mode(SETTINGS.screen_size)

    pygame.display.set_caption("TIPE")
    circuit = circuit_creation(SETTINGS)

    if SETTINGS.manual_control:
        manual_loop(screen, circuit)
    else:
        last_network = AI_loop(screen, circuit)
        if SETTINGS.autosave:
            BackupManager().create(network=last_network)

    pygame.quit()

    if SETTINGS.debug_mode:
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open("stats_report.log", "w", encoding="utf-8") as f:
            f.write(s.getvalue())


if __name__ == "__main__":
    main()
