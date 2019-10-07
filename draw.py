import pygame
import math
def circuit(screen: pygame.Surface, circuit: list):
	"""Création du circuit sur l'écran
	- screen (pygame.Surface): écran du jeu
	- circuit (list): liste de toutes les bordures (type Border)"""
	for i in circuit :
		pygame.draw.line(screen,i.color,i.start,i.end)


def car(screen, cars):
	for i in cars :
		A = rotate(i,[i.position[0] -20 ,i.position[1]-15])
		B = rotate(i,[i.position[0] +20 ,i.position[1]-15])
		C = rotate(i,[i.position[0] +20 ,i.position[1] +15])
		D = rotate(i,[i.position[0] -20 ,i.position[1] + 15])
		print(A)
		print(B)
		pygame.draw.line(screen,i.color,A,B,5)
		pygame.draw.line(screen,i.color,B,C,5)
		pygame.draw.line(screen,i.color,C,D,5)
		pygame.draw.line(screen,i.color,D,A,5)


def rotate(i,X):
	return [(X[0]- i.position[0]) * math.cos(math.radians(i.abs_rotation)) - (X[1]- i.position[1]) * math.sin(math.radians(i.abs_rotation))+i.position[0], 
           	 (X[0]+i.position[0]) * math.sin(math.radians(i.abs_rotation)) + (X[1]- i.position[1]) * math.cos(math.radians(i.abs_rotation))+i.position[1]]