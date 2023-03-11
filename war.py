from player import Player


class War:
    def __init__(self, home_clan_info: dict, enemy_clan_info: dict) -> None:
        self.home_clan_info = home_clan_info
        self.enemy_clan_info = enemy_clan_info
        self.players = []

        self.__parse_players()

    def __parse_players(self):
        for player_info in self.home_clan_info["members"]:
            player = Player(player_info["name"], player_info["tag"], player_info["townhallLevel"])
            player.add_war_participation(player_info, self.enemy_clan_info)
            self.players.append(player)
