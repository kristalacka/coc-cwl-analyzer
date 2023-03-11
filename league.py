from typing import Optional

from coc_api_service import CocApiService
from war import War


class League:
    def __init__(self, league_info: dict, clan_tag: str, api: Optional[CocApiService] = None):
        self.league_info = league_info
        self.clan_tag = clan_tag
        self.wars = []
        self.api = api or CocApiService()

        self.__parse_wars()

    def __parse_wars(self) -> None:
        for round in self.league_info["rounds"]:
            war_tags = round["warTags"]
            for tag in war_tags:
                war_info = self.api.get_war_info(tag)
                if war_info["state"] != "warEnded":
                    continue

                home_clan_info = None
                if war_info["clan"]["tag"] == self.clan_tag:
                    home_clan_info = war_info["clan"]
                    enemy_clan_info = war_info["opponent"]
                elif war_info["opponent"]["tag"] == self.clan_tag:
                    home_clan_info = war_info["opponent"]
                    enemy_clan_info = war_info["clan"]

                if not home_clan_info:
                    continue

                war = War(home_clan_info, enemy_clan_info)
                self.wars.append(war)
                break
