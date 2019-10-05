import pygame

def circuit(screen, circuit):
	for i in circuit :
		pygame.draw.line(screen,i.color,i.start,i.end)


def car():

	return