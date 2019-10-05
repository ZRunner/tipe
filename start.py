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
    screen = pygame.display.set_mode((800,800))
    pygame.display.set_caption("TIPE")
    circuit = [Border((10,10),(10,100)),Border((10,100),(70,200)),Border((70,200),(170,200))]

     

    running = True
    screen.fill((255,255,255))
    while running:
    	for event in pygame.event.get():
            if event.type == pygame.QUIT:
            	running = False 
    	draw.circuit(screen,circuit)
    	pygame.display.flip()


if __name__=="__main__":
    main()