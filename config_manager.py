"""
Gestionnaire de la configuration utilisateur

C'est dans ce fichier que se trouve la classe :class:`Config` enregistrant toutes les
configurations du programme, éditables dans le fichier 'settings.yaml'.
"""

import re
import json
from typing import Optional
from pygame import locals, Color
from ruamel.yaml import YAML
yaml = YAML(typ="safe", pure=True)


class Config():
    """
    Classe contenant la vérification utilisateur

    Elle est chargée depuis le fichier 'settings.yaml' par la fonction :func:`load_from_filename`,
    en utilisant le parseur YAML.

    :var float scale_x: 1: Echelle de l'écran en X
    :var float scale_y: 1: Echelle de l'écran en Y
    :var float scale_avg: 1: Echelle moyenne des formes (pour des cercles par exemple)
    :var float car_maniability: Maniabilité des voitures (nombre de degrés max par image dans
        un virage)
    :var int left_key: Touche du clavier pour tourner à gauche
    :var int right_key: Touche du clavier pour tourner à droite
    :var bool manual_control: Si le contrôle est manuel ou géré par les IAs
    :var Optional[str] display_rays: Méthode d'affichage du raytracing (None/'Ray'/'Cross')
    :var int cars_number: Nombre de voitures à utiliser en mode automatique
    :var str car_color: Couleur des voitures, en format hexa (mode manuel uniquement)
    :var List[int] screen_size: Taille de la fenêtre
    :var str theme: Thème graphique utilisé, parmi une liste définie (light/dark)
    :var dict colors: Liste de couleurs utilisées, définie par le thème graphique
    :var bool debug_mode: Utilisation du mode de débugage, qui liste les performances du programme
        et de chaque fonction appelée.
    :var bool autosave: Sauvegarde automatique du meilleure réseau neuronal à la fin du programme
    """

    def __init__(self, conf: dict):
        self.scale_x: float = 1
        self.scale_y: float = 1
        self.scale_avg: float = 1
        assert isinstance(conf["car_maniability"], (int, float)
                          ), "Invalid type for car_maniability"
        self.car_maniability: float = conf["car_maniability"]
        assert hasattr(locals, conf["left_key"]) and conf["left_key"].startswith(
            "K_"), "Invalid control for left_key"
        self.left_key = getattr(locals, conf["left_key"])
        assert hasattr(locals, conf["right_key"]) and conf["right_key"].startswith(
            "K_"), "Invalid control for right_key"
        self.right_key = getattr(locals, conf["right_key"])
        assert isinstance(conf["manual_control"],
                          bool), "Invalid type for manual_control"
        self.manual_control: bool = conf["manual_control"]
        assert conf["display_rays"] in ["None", "Ray",
                                        "Cross"], "Invalid option for display_rays"
        self.display_rays: Optional[str] = conf["display_rays"]
        if self.display_rays == "None":
            self.display_rays = None
        assert isinstance(conf["cars_number"],
                          int), "Invalid type for cars_number"
        self.cars_number: int = conf["cars_number"]
        assert re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                        conf["car_color"]), "Invalid hex code for car_color"
        self.car_color: str = conf["car_color"]
        assert isinstance(conf["screen_size"], list) and len(conf["screen_size"]) == 2 and all(
            isinstance(i, int) for i in conf["screen_size"]), "Invalid formar for screen_size"
        self.screen_size: [int, int] = conf["screen_size"]
        try:
            with open("themes/"+conf["theme"].lower()+".json", "r", encoding="utf8") as themefile:
                self.colors: dict = json.load(themefile)
        except FileNotFoundError:
            raise Exception("Invalid option for theme")
        self.theme: str = conf["theme"]
        assert isinstance(conf["debug_mode"],
                          bool), "Invalid type for debug_mode"
        self.debug_mode: bool = conf["debug_mode"]
        assert isinstance(conf["autosave"],
                          bool), "Invalid type for autosave"
        self.autosave: bool = conf["autosave"]
        self.treat_colors()
        self.calc_scale()

    def treat_colors(self):
        for k, v in self.colors.items():
            if isinstance(v, str):
                self.colors[k] = Color(v)
            elif isinstance(v, list):
                self.colors[k] = [Color(i) for i in v]

    def calc_scale(self):
        self.scale_x = self.screen_size[0]/1200
        self.scale_y = self.screen_size[1]/700
        self.scale_avg = (self.scale_x + self.scale_y) / 2


def load_from_filename(filename: str) -> Config:
    """Charge le fichier de configuration pour initialiser une nouvelle classe Config

    Parameters
    ----------
    filename:
        Nom du fichier de configuration
    """
    with open(filename, 'r', encoding='utf8') as myfile:
        result = yaml.load(myfile)
    return Config(result)
