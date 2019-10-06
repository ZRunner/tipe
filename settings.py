import pygame

# Touches de contrôle de la voiture, et vecteurs mouvements associés
move_keys = {pygame.K_LEFT: pygame.math.Vector2(-1,0),
             pygame.K_RIGHT: pygame.math.Vector2(1,0),
             pygame.K_UP: pygame.math.Vector2(0,1),
             pygame.K_DOWN: pygame.math.Vector2(0,-1)}

# Contrôle manuel de la voiture
manual_control = True

# Nombre de voitures lors du mode automatique
cars_number = 1

# Images par seconde
fps = 30
