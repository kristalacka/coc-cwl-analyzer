import os
import pickle
from collections import Counter, defaultdict
from dataclasses import dataclass

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from utils.coc_api_service import CocApiService
from utils.league import League
from utils.player import Player


@dataclass
class LeaguePerformance:
    score: float = 0.0
    wars_participated: int = 0
    wars_attacked: int = 0


class CwlAnalyzer:
    def __init__(self, missed_attack_penalty: float = 100.0, number_difference_check: bool = False):
        self.missed_attack_penalty = missed_attack_penalty
        self.number_difference_check = number_difference_check
        self.api = CocApiService()

    def analyze(self, clan_tag: str, clan_alias: str, clan_name: str, month: str) -> tuple[Player, LeaguePerformance]:
        player_score_map: dict[Player, LeaguePerformance] = defaultdict(lambda: LeaguePerformance())

        results_pickle_path = f"results/{month}/{clan_alias}.p"
        if os.path.exists(results_pickle_path):
            league = pickle.load(open(results_pickle_path, "rb"))
        else:
            war_league_info = self.api.get_cwl_info(clan_tag)
            league = League(war_league_info, clan_tag, self.api)
            pickle.dump(league, open(results_pickle_path, "wb"))

        for war in league.wars:
            for player in war.players:
                player_score_map[player].score += self.__calculate_player_score(player)
                player_score_map[player].wars_participated += 1
                player_score_map[player].wars_attacked += 1 if not player.missed_attack else 0

        self.__plot_stats(league, clan_alias, clan_name, month)

        players = sorted(player_score_map.items(), key=lambda x: x[1].score, reverse=True)
        print(f"{clan_name} MVPs: {', '.join([player[0].name for player in players[:3]])}")
        return players

    def __calculate_player_score(self, player) -> float:
        # good score - 100, points are deducted based on various factors.

        if player.missed_attack:
            return -abs(self.missed_attack_penalty)

        town_hall_difference = player.performance.attacker_th - player.performance.defender_th
        number_difference = player.performance.attacker_number - player.performance.defender_number
        stars = player.performance.stars
        destruction = player.performance.destruction

        if town_hall_difference == 0:  # attacking the same town hall
            return self.__calculate_equal_th_score(number_difference, stars, destruction)
        elif town_hall_difference < 0:  # attacking up
            return self.__calculate_higher_th_score(number_difference, stars, destruction, town_hall_difference)
        else:  # dip
            return self.__calculate_lower_th_score(number_difference, stars, destruction, town_hall_difference)

    def __calculate_equal_th_score(self, number_difference: int, stars: int, destruction: float) -> float:
        # return stars - 3

        if stars == 3:
            score = 100.0
            if number_difference >= 0:
                return score

            return score - number_difference if self.number_difference_check else score

        if stars == 2:
            score = 80.0

            return destruction * score / 100.0

        if stars == 1:
            score = 20.0

            return destruction * score / 100.0

        return 0.0

    def __calculate_higher_th_score(
        self, number_difference: int, stars: int, destruction: float, town_hall_difference: int
    ) -> float:
        # return stars - 2

        if stars == 3:
            score = 100.0
            if number_difference >= 0:
                return score

            return score - number_difference if self.number_difference_check else score

        if stars == 2:
            score = 100.0

            return destruction * score / 70.0 + town_hall_difference * 10

        if stars == 1:
            score = 50.0

            return destruction * score / 100.0

        return 0.0

    def __calculate_lower_th_score(
        self, number_difference: int, stars: int, destruction: float, town_hall_difference: int
    ) -> float:
        # return stars - 3

        if stars == 3:
            score = 100.0
            if number_difference >= 0:
                return score

            score -= abs(town_hall_difference) * 10
            return score - number_difference if self.number_difference_check else score

        if stars == 2:
            score = 50.0

            return destruction * score / 100.0

        if stars == 1:
            score = 10.0

            return destruction * score / 100.0

        return -20.0

    def __plot_stats(self, league: League, clan_alias: str, clan_name: str, month: str):
        COLOR = "white"
        mpl.rcParams["text.color"] = COLOR
        mpl.rcParams["axes.labelcolor"] = COLOR
        mpl.rcParams["xtick.color"] = COLOR
        mpl.rcParams["ytick.color"] = COLOR
        mpl.rcParams["font.weight"] = "bold"

        font_path = "fonts/supercell-magic.ttf"
        font_properties = fm.FontProperties(fname=font_path)
        title_kwargs = {"fontproperties": font_properties, "fontsize": 12}
        label_kwargs = {"fontweight": "bold"}

        star_counter = Counter()
        destruction = []
        missed_attacks = 0

        for war in league.wars:
            for player in war.players:
                if player.missed_attack:
                    missed_attacks += 1

                if player.performance:
                    star_counter[player.performance.stars] += 1
                    destruction.append(player.performance.destruction)

        plt.hist(destruction, bins=20, range=(0, 100), color="bisque")
        plt.title(f"{clan_name} - CWL destruction %", **title_kwargs)
        plt.xlabel("Destruction (%)", **label_kwargs)
        plt.ylabel("Attack count", **label_kwargs)
        plt.savefig(f"results/{month}/{clan_alias}_destruction.png", transparent=True)  # TODO: use main project path
        plt.clf()

        plt.hist([attack for attack in destruction if attack < 100], bins=20, range=(0, 100), color="bisque")
        plt.title(f"{clan_name} - CWL destruction % (3 stars omitted)", **title_kwargs)
        plt.xlabel("Destruction (%)", **label_kwargs)
        plt.ylabel("Attack count", **label_kwargs)
        plt.savefig(f"results/{month}/{clan_alias}_destruction_no_3_stars.png", transparent=True)
        plt.clf()

        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return "{p:.2f}%  ({v:d})".format(p=pct, v=val)

            return my_autopct

        star_counter = dict(star_counter)
        star_counter = {k: v for k, v in sorted(star_counter.items(), key=lambda item: item[0], reverse=True)}
        star_counter["missed"] = missed_attacks

        pie_vals = [float(v) for v in star_counter.values()]
        colors = {
            3: "tab:blue",
            2: "tab:green",
            1: "tab:orange",
            0: "tab:red",
            "missed": "tab:gray",
        }
        plt.pie(
            pie_vals,
            labels=[f"{key}★" if isinstance(key, int) else key for key in star_counter.keys()],
            autopct=make_autopct(pie_vals),
            colors=[colors[key] for key in star_counter.keys()],
            explode=[0.1 if key == 3 else 0 for key in star_counter.keys()],
        )
        plt.title(f"{clan_name} - CWL stars", **title_kwargs)
        plt.savefig(f"results/{month}/{clan_alias}_stars.png", transparent=True)
        plt.clf()
