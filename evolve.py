"""
Fichier contenant les fonctions de mutation et d'évolution

C'est dans ce fichier que l'algorithme de mutation dit "de Darwin" est défini, utilisant une
combinaison de mutations et de mélanges pour créer une nouvelle génération de réseaux neuronaux
à partir des meilleurs de l'ancienne génération.
"""

from classes import Car, Network
from pygame import Color
from copy import deepcopy as copy
from typing import List
import random


def mutation(networks: List[Network]) -> List[Network]:
    """Génère une mutation sur un réseau neuronal

    Chaque neurone a une faible probabilité de voir son poids modifié à une valeur aléatoire, entre
    -2.0 et 4.0, ainsi que son bias, entre -1.0 et 1.0

    Parameters
    ----------
    networks:
        Liste de réseaux neuronaux à modifier
    """
    mutation_rate = 0.15
    for net in networks:
        for neuron in net.I_layer:
            if random.random() < mutation_rate:
                neuron.bias = random.random()*2 - 1
            for i in range(len(neuron.weight)):
                if random.random() < mutation_rate:
                    neuron.weight[i] = random.random()*4 - 2
        for neuron in net.layer_2:
            if random.random() < mutation_rate:
                neuron.bias = random.random()*2 - 1
            for i in range(len(neuron.weight)):
                if random.random() < mutation_rate:
                    neuron.weight[i] = random.random()*4 - 2
        for neuron in net.layer_3:
            if random.random() < mutation_rate:
                neuron.bias = random.random()*2 - 1
            for i in range(len(neuron.weight)):
                if random.random() < mutation_rate:
                    neuron.weight[i] = random.random()*4 - 2
        for neuron in net.layer_4:
            if random.random() < mutation_rate:
                neuron.bias = random.random()*2 - 1
            for i in range(len(neuron.weight)):
                if random.random() < mutation_rate:
                    neuron.weight[i] = random.random()*4 - 2


def swap(n1: Network, n2: Network) -> [Network, Network]:
    """
    Mélange les composantes de deux réseaus neuronaux

    Chaque neurone du réseau 1 a 60% de chance de se faire échanger avec le neurone correspondant
    du réseau 2.

    Parameters
    ----------
    n1:
        Permier réseau neuronal
    n2:
        Second réseau neuronal

    Returns
    -------
    [Network, Network]:
        Les deux réseaux une fois mélangés
    """
    swap_rate = 0.6
    for i, neuron in enumerate(n1.I_layer):
        if random.random() < swap_rate:
            t = neuron.bias
            neuron.bias = n2.I_layer[i].bias
            n2.I_layer[i].bias = t
        for j in range(len(neuron.weight)):
            if random.random() < swap_rate:
                n2.I_layer[i].weight[j], neuron.weight[j] = neuron.weight[j], n2.I_layer[i].weight[j]
    for i, neuron in enumerate(n1.layer_2):
        if random.random() < swap_rate:
            t = neuron.bias
            neuron.bias = n2.layer_2[i].bias
            n2.layer_2[i].bias = t
        for j in range(len(neuron.weight)):
            if random.random() < swap_rate:
                n2.layer_2[i].weight[j], neuron.weight[j] = neuron.weight[j], n2.layer_2[i].weight[j]
    for i, neuron in enumerate(n1.layer_3):
        if random.random() < swap_rate:
            t = neuron.bias
            neuron.bias = n2.layer_3[i].bias
            n2.layer_3[i].bias = t
        for j in range(len(neuron.weight)):
            if random.random() < swap_rate:
                n2.layer_3[i].weight[j], neuron.weight[j] = neuron.weight[j], n2.layer_3[i].weight[j]
    for i, neuron in enumerate(n1.layer_4):
        if random.random() < swap_rate:
            t = neuron.bias
            neuron.bias = n2.layer_4[i].bias
            n2.layer_4[i].bias = t
        for j in range(len(neuron.weight)):
            if random.random() < swap_rate:
                n2.layer_4[i].weight[j], neuron.weight[j] = neuron.weight[j], n2.layer_4[i].weight[j]
    return (n1, n2)


def darwin(networks: List[Network]) -> List[Network]:
    """Applique le modèle d'évolution dite "de Darwin" à une population de réseaux neuronaux

    Les réseaux sont triés selon leurs scores, puis les meilleurs d'entre eux sont utilisés pour
    créer d'autres réseaux, remplaçant les moins bons. Enfin, la plus grande partie des réseaux
    subit un phénomène de mutation altérant de manière aléatoire certaines de leurs valeurs.

    Parameters
    ----------
    networks:
        Liste des réseaux neuronaux sur lesquels appliquer l'évolution

    Returns
    -------
    List[Network]:
        Les réseaux unef fois édités
    """
    rank = sorted(networks, key=lambda net: net.score, reverse=True)  # first is best
    new_gen = [copy(rank[0]), copy(rank[1])]
    for _ in range(0, max(4, len(rank)-4), 2):
        new_gen += swap(copy(rank[0]), copy(rank[1]))
    if len(new_gen) < len(rank):
        new_gen += [Network(copy(networks[i].car)) for i in range(len(new_gen), len(rank))]
    for x in new_gen:
        x.car.abs_rotation = 0
    mutation(new_gen[2:])
    return new_gen[:len(networks)]
