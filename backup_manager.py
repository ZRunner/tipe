from classes import *
from typing import List
import json


class BackupManager():
    def __init__(self, filename: str = "backup"):
        self.filename = filename
        if not self.filename.endswith(".json"):
            self.filename += ".json"

    def _neuron(self, neur: Neuron) -> dict:
        return {
            "value": neur.value,
            "weight": neur.weight,
            "bias": neur.bias
        }

    def _network(self, net: Network) -> dict:
        return {
            "layers": [
                len(net.I_layer),
                len(net.layer_2),
                len(net.layer_3),
                len(net.layer_4)
            ],
            "neurons": [
                [self._neuron(x) for x in net.I_layer],
                [self._neuron(x) for x in net.layer_2],
                [self._neuron(x) for x in net.layer_3],
                [self._neuron(x) for x in net.layer_4]
            ]
        }

    def _border(self, border: Border) -> dict:
        return {
            "color": border.color,
            "start": border.start,
            "end": border.end
        }

    def create(self, *, network: Network = None, networks: List[Network] = None,
               circuit: List[Border] = None):
        if network is None and networks is None and circuit is None:
            raise ValueError("At least one argument is required")
        data = {
            "network": None,
            "networks": None,
            "circuit": None
        }
        if network:
            data["network"] = self._network(network)
        if networks:
            data["networks"] = [self._network(net) for net in networks]
        if circuit:
            data["circuit"] = [self._border(b) for b in circuit]
        with open(self.filename, "w", encoding="utf-8") as myfile:
            json.dump(data, myfile)
        print("Sauvegarde terminée")

    def load(self) -> dict:
        try:
            with open(self.filename, "r", encoding="utf-8") as myfile:
                data = json.load(myfile)
            return data
        except FileNotFoundError:
            return {
                "network": None,
                "networks": None,
                "circuit": None
            }
