import pygame

# Maniabilité du véhicule (nombre de degrés par fps dans un virage)
car_maniability = 1

# Touches de contrôle de la voiture, gauche et droite
left_key = pygame.K_LEFT
right_key = pygame.K_RIGHT

# Contrôle manuel de la voiture
manual_control = True

# Nombre de voitures lors du mode automatique
cars_number = 1

# Images par seconde

fps = 30

# Taille de la fenêtre
try :
	screen_size = [int(pygame.display.Info().current_h * 0.7)]*2
except :
	screen_size = [800]*2
