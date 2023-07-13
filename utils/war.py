from statistics import mean
from typing import Optional

from utils.player import Player


class War:
    def __init__(self, home_clan_info: dict, enemy_clan_info: dict, ended: bool = True) -> None:
        self.home_clan_info = home_clan_info
        self.enemy_clan_info = enemy_clan_info
        self.ended = ended
        self.players: list[Player] = []

        self.__parse_players()

    def get_average_th_level(self) -> tuple[float, float]:
        home_th_levels = [player_info["townhallLevel"] for player_info in self.home_clan_info["members"]]
        enemy_th_levels = [player_info["townhallLevel"] for player_info in self.enemy_clan_info["members"]]
        return mean(home_th_levels), mean(enemy_th_levels)

    def get_won(self) -> Optional[bool]:
        if not self.ended:
            return None

        if self.home_clan_info["stars"] == self.enemy_clan_info["stars"]:
            return self.home_clan_info["destructionPercentage"] > self.enemy_clan_info["destructionPercentage"]

        return self.home_clan_info["stars"] > self.enemy_clan_info["stars"]

    def get_stars(self) -> tuple[int, int]:
        won = self.get_won()
        if won is None:
            return self.home_clan_info["stars"], self.enemy_clan_info["stars"]

        return self.home_clan_info["stars"] + int(won) * 10, self.enemy_clan_info["stars"] + int(not won) * 10

    def get_destruction(self) -> tuple[float, float]:
        clan1_destruction, clan2_destruction = 0.0, 0.0
        for player in self.home_clan_info["members"]:
            if player.get("attacks"):
                clan1_destruction += player["attacks"][0]["destructionPercentage"]

        for player in self.enemy_clan_info["members"]:
            if player.get("attacks"):
                clan2_destruction += player["attacks"][0]["destructionPercentage"]

        return clan1_destruction, clan2_destruction

    def __parse_players(self):
        for player_info in self.home_clan_info["members"]:
            player = Player(player_info["name"], player_info["tag"], player_info["townhallLevel"])
            player.add_war_participation(player_info, self.enemy_clan_info, self.ended)
            self.players.append(player)
