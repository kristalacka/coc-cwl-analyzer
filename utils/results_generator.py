import json
from enum import Enum
from io import BytesIO
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from utils.coc_api_service import CocApiService


class PromotionStatus(Enum):
    PROMOTED = "Promoted"
    DEMOTED = "Demoted"
    NO_CHANGE = "No Change"


class ResultsGenerator:
    def __init__(
        self,
        month: str,
        clan: str,
        clan_tag: str,
        clan_name: str,
        promotion_status: PromotionStatus,
        comment: Optional[str] = None,
    ) -> None:
        self.month = month.upper()
        self.clan = clan
        self.clan_tag = clan_tag
        self.clan_name = clan_name
        self.promotion_status = promotion_status
        self.comment = comment or ""

    def generate(self):
        background = Image.open("media/background.png")
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.7)

        clan_info = CocApiService().get_clan_info(self.clan_tag)
        self.clan_league = clan_info["warLeague"]["name"]
        clan_badge_url = clan_info["badgeUrls"]["medium"]

        with open(f"response_samples/leagues.json", "r") as f:
            leagues = json.loads(f.read())

        league_icon_url = next(
            (league["iconUrls"]["medium"] for league in leagues["items"] if league["name"] == self.clan_league), None
        )
        league = self.__get_image_from_url(league_icon_url)
        clan_badge = self.__get_image_from_url(clan_badge_url)

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
        background = self.__overlay_image(
            background,
            league,
            offset=(center[0], center[1] - 150),
        )
        if self.promotion_status == PromotionStatus.NO_CHANGE:
            result_text = "No change in league"
            result_color = (255, 255, 255)
        elif self.promotion_status == PromotionStatus.PROMOTED:
            result_text = f"Promoted to {self.clan_league}"
            result_color = (220, 255, 220)
        elif self.promotion_status == PromotionStatus.DEMOTED:
            result_text = f"Demoted to {self.clan_league}"
            result_color = (255, 220, 220)

        return self.__write_text(
            background,
            result_text,
            size=48,
            offset=(0, 300),
            fill=result_color,
        )

    def __write_clan_name(self, background: Image):
        return self.__write_text(
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
        background = self.__write_text(
            background,
            f"Average Friendly TH: {round(friendly_th ,2)}",
            offset=(0, 600),
            size=32,
        )
        return self.__write_text(
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
        return self.__overlay_image(
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
        background = self.__overlay_image(
            background,
            destruction,
            offset=(center[0] - 500, center[1] + 300),
        )

        size = 1.5
        img_w, img_h = stars.size
        stars = stars.resize((int(img_w * size), int(img_h * size)))
        img_w, img_h = stars.size
        center = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
        background = self.__overlay_image(
            background,
            stars,
            offset=(center[0] + 500, center[1] + 300),
        )

        return self.__write_text(
            background,
            self.comment,
            offset=(0, 1200),
            size=56,
        )

    def __get_image_from_url(self, url: str) -> Image:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))

    def __overlay_image(self, background: Image, overlay: Image, offset: tuple[int] = (0, 0)):
        background.paste(overlay, offset, overlay)
        return background

    def __write_text(
        self,
        background: Image,
        text: str,
        size: int = 64,
        offset: tuple[int] = (0, 0),
        fill: tuple[int] = (255, 255, 255),
        stroke_width: int = 2,
        stroke_fill: tuple[int] = (0, 0, 0),
    ):
        bg_w, bg_h = background.size
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("fonts/supercell-magic.ttf", size)
        _, _, w, h = draw.textbbox(offset, text, font=font)
        draw.text(
            ((bg_w - w) / 2, (bg_h - h) / 2),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        return background
