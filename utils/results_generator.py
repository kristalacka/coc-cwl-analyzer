import json
from typing import Optional

from PIL import Image, ImageEnhance

from utils.cwl_analyzer import CwlAnalyzer
from utils.image_utils import ImageUtils
from utils.league import PromotionStatus


class ResultsGenerator:
    def __init__(
        self,
        month: str,
        clan: str,
        clan_tag: str,
        clan_name: str,
        analyzer: CwlAnalyzer,
        comment: Optional[str] = None,
    ) -> None:
        self.month = month.upper()
        self.clan = clan
        self.clan_tag = clan_tag
        self.clan_name = clan_name
        self.analyzer = analyzer
        self.comment = comment or ""

    def generate(self):
        background = Image.open("media/background.png")
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.7)

        clan_badge_url = self.analyzer.league.clan_info["badgeUrls"]["medium"]

        with open("response_samples/leagues.json", "r") as f:
            leagues = json.loads(f.read())

        league_icon_url = next(
            (
                league["iconUrls"]["medium"]
                for league in leagues["items"]
                if league["name"] == self.analyzer.league.clan_league
            ),
            None,
        )
        league = ImageUtils.get_image_from_url(league_icon_url)
        clan_badge = ImageUtils.get_image_from_url(clan_badge_url)

        background = self.__overlay_league(background, league)
        background = self.__overlay_badge(background, clan_badge)
        background = self.__write_clan_name(background)
        background = self.__overlay_results(background)
        background = self.__write_avg_th(background)

        background.save(f"results/{self.month}/{self.clan}_overview.png")

    def __overlay_league(self, background: Image, league: Image):
        bg_w, bg_h = background.size
        img_w, img_h = league.size
        league = league.resize((int(img_w / 1.5), int(img_h / 1.5)))
        img_w, img_h = league.size

        center = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        background = ImageUtils.overlay_image(
            background,
            league,
            offset=(center[0], center[1] - 150),
        )
        if self.analyzer.league.promotion_status == PromotionStatus.NO_CHANGE:
            # result_text = "No change in league"
            result_color = (255, 255, 255)
        elif self.analyzer.league.promotion_status == PromotionStatus.PROMOTED:
            # result_text = f"Promoted to {self.clan_league}"
            result_color = (220, 255, 220)
        elif self.analyzer.league.promotion_status == PromotionStatus.DEMOTED:
            # result_text = f"Demoted to {self.clan_league}"
            result_color = (255, 220, 220)

        result_text = f"Placed #{self.analyzer.league.placement}"

        return ImageUtils.write_text(
            background,
            result_text,
            size=48,
            offset=(0, 300),
            fill=result_color,
        )

    def __write_clan_name(self, background: Image):
        return ImageUtils.write_text(
            background,
            self.clan_name,
            offset=(0, 800),
            size=64,
        )

    def __write_avg_th(self, background: Image):
        with open(f"results/{self.month}/{self.clan}_town_halls.csv", "r") as f:
            data = f.read()

        friendly_th, enemy_th = data.split(",")
        friendly_th = float(friendly_th)
        enemy_th = float(enemy_th)
        background = ImageUtils.write_text(
            background,
            f"Average Friendly TH: {round(friendly_th ,2)}",
            offset=(0, 600),
            size=32,
        )
        return ImageUtils.write_text(
            background,
            f"Average Enemy TH: {round(enemy_th, 2)}",
            offset=(0, 500),
            size=32,
        )

    def __overlay_badge(self, background: Image, badge: Image):
        bg_w, bg_h = background.size
        img_w, img_h = badge.size
        badge = badge.resize((int(img_w * 1.5), int(img_h * 1.5)))
        img_w, img_h = badge.size

        center = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        return ImageUtils.overlay_image(
            background,
            badge,
            offset=(center[0], center[1] - 400),
        )

    def __overlay_results(self, background: Image):
        size = 1.3
        destruction = Image.open(f"results/{self.month}/{self.clan}_destruction.png")
        stars = Image.open(f"results/{self.month}/{self.clan}_stars.png")

        bg_w, bg_h = background.size
        img_w, img_h = destruction.size
        destruction = destruction.resize((int(img_w * size), int(img_h * size)))
        img_w, img_h = destruction.size

        center = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        background = ImageUtils.overlay_image(
            background,
            destruction,
            offset=(center[0] - 500, center[1] + 300),
        )

        size = 1.5
        img_w, img_h = stars.size
        stars = stars.resize((int(img_w * size), int(img_h * size)))
        img_w, img_h = stars.size
        center = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        background = ImageUtils.overlay_image(
            background,
            stars,
            offset=(center[0] + 500, center[1] + 300),
        )

        return ImageUtils.write_text(
            background,
            self.comment,
            offset=(0, 1200),
            size=56,
        )
