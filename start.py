import draw
import key
from classes import *

import pygame


def main():
    print("""Lancement du programme

    Assurez-vous que toutes les dépendances utilisées soient installées sur votre ordinateur ;
    si besoin entrez `pip install -r requirements.txt` dans votre console
    """)

    pygame.init()
    import settings # doit ABSOLUMENT être appelé *après* le init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(settings.screen_size)
    pygame.display.set_caption("TIPE")
    circuit = [Border((10, 10), (10, 100)), 
            Border((10, 100), (70, 200)), 
            Border((70, 200), (170, 200))
            ]
    if settings.manual_control:
        cars = [Car()]
    else:
        cars = [Car() for _ in range(settings.cars_number)]

    running = True
    screen.fill((255, 255, 255))
    dt = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw.circuit(screen, circuit)
        pygame.display.flip()
        # Gestion du mouvement de la voiture
        if settings.manual_control:
            pressed = pygame.key.get_pressed()
            delta = dt * settings.fps / 1000
            if pressed[settings.left_key]:
                cars[0].abs_rotation -= settings.car_maniability * delta
            if pressed[settings.left_key]:
                cars[0].abs_rotation += settings.car_maniability * delta
            cars[0].apply_vector(cars[0].direction_vector())
            # print(cars[0].position)
        dt = clock.tick(settings.fps)
    pygame.quit()


if __name__ == "__main__":
    main()
