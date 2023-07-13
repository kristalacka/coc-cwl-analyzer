import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from utils.coc_api_service import CocApiService
from utils.war import War

logger = logging.getLogger("league")


class PromotionStatus(Enum):
    PROMOTED = "Promoted"
    DEMOTED = "Demoted"
    NO_CHANGE = "No Change"


@dataclass
class ClanStanding:
    stars: int
    destruction: float


# number of clans promoted per league
PROMOTIONS = {
    r"Gold.*": 2,
    r"Crystal I": 1,
    r"Crystal.*": 2,
    r"Master.*": 1,
    r"Champion.*": 1,
}

# number of clans demoted per league
DEMOTIONS = {
    r".*": 2,
}


class League:
    def __init__(self, league_info: dict, clan_tag: str, api: Optional[CocApiService] = None):
        self.league_info = league_info
        self.clan_tag = clan_tag
        self.wars: list[War] = []
        self.api = api or CocApiService()

        self.clan_info = self.api.get_clan_info(self.clan_tag)
        self.clan_league = self.clan_info["warLeague"]["name"]

        self.__parse_wars()
        self.standings = self.__get_standings()
        self.__get_promotions()

    def __get_standings(self) -> list[dict]:
        # sort by stars, then destruction
        clan_totals = defaultdict(lambda: ClanStanding(0, 0.0))
        for war in self.wars:
            home_stars, enemy_stars = war.get_stars()
            home_destruction, enemy_destruction = war.get_destruction()

            clan_totals[war.home_clan_info["tag"]].stars += home_stars
            clan_totals[war.home_clan_info["tag"]].destruction += home_destruction

            clan_totals[war.enemy_clan_info["tag"]].stars += enemy_stars
            clan_totals[war.enemy_clan_info["tag"]].destruction += enemy_destruction

        standings = sorted(
            [
                {
                    "tag": tag,
                    "stars": clan_totals[tag].stars,
                    "destruction": clan_totals[tag].destruction,
                }
                for tag in clan_totals
            ],
            key=lambda clan: (clan["stars"], clan["destruction"]),
            reverse=True,
        )
        return standings

    def __parse_wars(self) -> None:
        for round in self.league_info["rounds"]:
            war_tags = round["warTags"]
            for tag in war_tags:
                war_info = self.api.get_war_info(tag)
                ended = war_info["state"] == "warEnded"

                home_clan_info = None
                if war_info["opponent"]["tag"] == self.clan_tag:
                    home_clan_info = war_info["opponent"]
                    enemy_clan_info = war_info["clan"]
                else:
                    home_clan_info = war_info["clan"]
                    enemy_clan_info = war_info["opponent"]

                # if not home_clan_info:
                #     continue

                war = War(home_clan_info, enemy_clan_info, ended=ended)
                self.wars.append(war)

    def __get_promotions(self):
        promotions = next((value for regex, value in PROMOTIONS.items() if re.match(regex, self.clan_league)), None)
        demotions = next((value for regex, value in DEMOTIONS.items() if re.match(regex, self.clan_league)), None)
        self.placement = next(
            (i + 1 for i, clan in enumerate(self.standings) if clan["tag"] == self.clan_tag),
            None,
        )
        self.promotion_status = self.__get_promotion_status(promotions, demotions)

    def __get_promotion_status(self, promotions: int, demotions: int) -> PromotionStatus:
        if self.placement is None:
            return PromotionStatus.NO_CHANGE

        if self.placement <= promotions:
            return PromotionStatus.PROMOTED
        elif self.placement > len(self.standings) - demotions:
            return PromotionStatus.DEMOTED
        else:
            return PromotionStatus.NO_CHANGE
