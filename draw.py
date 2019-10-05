import pygame

def circuit(screen: pygame.Surface, circuit: list):
	"""Création du circuit sur l'écran
	- screen (pygame.Surface): écran du jeu
	- circuit (list): liste de toutes les bordures (type Border)"""
	for i in circuit :
		pygame.draw.line(screen,i.color,i.start,i.end)


def car():

	return