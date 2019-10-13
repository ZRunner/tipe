import pygame
import math


def circuit(screen: pygame.Surface, circuit: list):
    """Création du circuit sur l'écran
    - screen (pygame.Surface): écran du jeu
    - circuit (list): liste de toutes les bordures (type Border)"""
    for i in circuit:
        pygame.draw.line(screen, i.color, i.start, i.end)


def car(screen: pygame.Surface, cars: list):
    """Dessine les voitures sur le circuit
    - screen (pygame.Surface): écran du jeu
    - cars (list): liste de toutes les voitures (type Car)"""
    for car in cars:
        A =[car.position[0] - 20, car.position[1] - 15]
        B = [car.position[0] + 20, car.position[1] - 15]
        C = [car.position[0] + 20, car.position[1] + 15]
        D = [car.position[0] - 20, car.position[1] + 15]
        pygame.draw.line(screen, car.color, A, B, 5)
        pygame.draw.line(screen, car.color, B, C, 5)
        pygame.draw.line(screen, car.color, C, D, 5)
        pygame.draw.line(screen, car.color, D, A, 5)


def rotate(car, X):
	"""Applique une rotation à un point selon la position et la rotation de la voiture
	- car (Car): voiture de référence
	- X (tuple): position du point"""
	return [(X[0] - car.position[0]) * math.cos(math.radians(car.abs_rotation)) - (X[1] - car.position[1]) * math.sin(math.radians(car.abs_rotation))+car.position[0],
            (X[0] + car.position[0]) * math.sin(math.radians(car.abs_rotation)) + (X[1] - car.position[1]) * math.cos(math.radians(car.abs_rotation))+car.position[1]]
