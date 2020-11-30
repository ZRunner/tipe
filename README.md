# tipe
Repo utilisé pour le projet TIPE sur le thème "Voitures autonomes"

Le but de ce projet était de créer une **Intelligence Artificielle** capable de piloter une voiture dans un **circuit fermé**. La voiture devait être capable d'aller jusqu'à l'arrivée *sans heurter aucun mur*, et de la manière la plus rapide possible.

Pour cela, nous avons utilisé un **réseau neuronal** basique sans évolution (nombre de neurones constant), unique pour chaque voiture, qui prenait en entrée la distance des prochains murs via un *raycasting* ainsi que la vitesse et l'angle actuel de la voiture, et qui ressortait la *nouvelle vitesse* et la rotation de la voiture.

En envoyant *plusieurs dizaines* de voitures en même temps sur le circuit, puis en prenant les meilleurs éléments pour **les mélanger** et créer des nouvelles voitures, nous réussissons à voir un résultat **avant le dixième tour**. La **génération procédurale**, et donc aléatoire, du circuit permet d'avoir une plus grande diversité du terrain, et ainsi *d'étudier le comportement* sur un terrain d'une voiture entraînée sur un autre terrain.
