from dataclasses import dataclass
from typing import Optional


@dataclass
class Performance:
    attacker_th: int
    defender_th: int
    attacker_number: int
    defender_number: int
    stars: int
    destruction: float


class Player:
    def __init__(self, name: str, tag: str, town_hall: int) -> None:
        self.name = name
        self.tag = tag
        self.town_hall = town_hall
        self.missed_attack = False

        self.performance = None

    def add_war_participation(self, player_info: dict, enemy_info: dict) -> None:
        attacks = player_info.get("attacks", [])
        if not attacks:
            self.missed_attack = True
            return

        attack = attacks[0]

        attacker_th = self.town_hall
        attacker_number = player_info["mapPosition"]
        stars = attack["stars"]
        destruction = attack["destructionPercentage"]

        defender_th = -1
        defender_number = -1
        for member in enemy_info["members"]:
            if member["tag"] == attack["defenderTag"]:
                defender_th = member["townhallLevel"]
                defender_number = member["mapPosition"]
                break

        self.performance = Performance(attacker_th, defender_th, attacker_number, defender_number, stars, destruction)

    def __hash__(self) -> int:
        return hash(self.tag)

    def __eq__(self, __o: "Player") -> bool:
        return self.tag == __o.tag
