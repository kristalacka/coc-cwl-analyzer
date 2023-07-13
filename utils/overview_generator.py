import json
from typing import Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from utils.cwl_analyzer import CwlAnalyzer
from utils.image_utils import ImageUtils
from utils.league import PromotionStatus


class OverviewGenerator:
    def __init__(
        self,
        month: str,
        clans: dict[str, CwlAnalyzer],
        comment: Optional[str] = None,
    ) -> None:
        self.month = month.upper()
        self.clans = clans
        self.comment = comment or ""

    def generate(self):
        background = Image.open("media/background-2.png")
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.7)

        with open("response_samples/leagues.json", "r") as f:
            leagues = json.loads(f.read())

        self.clan_count = len(self.clans)

        for i, (clan_alias, analyzer) in enumerate(self.clans.items()):
            clan_badge_url = analyzer.league.clan_info["badgeUrls"]["medium"]

            league_icon_url = next(
                (
                    league["iconUrls"]["medium"]
                    for league in leagues["items"]
                    if league["name"] == analyzer.league.clan_league
                ),
                None,
            )
            league = ImageUtils.get_image_from_url(league_icon_url)
            clan_badge = ImageUtils.get_image_from_url(clan_badge_url)

            background = self.__overlay_league(background, league, analyzer, i)
            background = self.__overlay_badge(background, clan_badge, i)
            background = self.__write_clan_name(background, analyzer, i)
            background = self.__overlay_results(background, clan_alias, i)

        background.save(f"results/{self.month}/all_overview.png")

    def __overlay_league(self, background: Image, league: Image, analyzer: CwlAnalyzer, clan_index: int):
        bg_w, bg_h = background.size
        img_w, img_h = league.size
        league = league.resize((int(img_w / 5), int(img_h / 5)))
        img_w, img_h = league.size

        x_spacing = bg_w // (self.clan_count + 1)  # Calculate the spacing between leagues
        x_coord = x_spacing * (clan_index + 1)  # Calculate the x-coordinate for the current league
        x_coord -= img_w // 2  # Adjust the coordinate to center the league horizontally

        background = ImageUtils.overlay_image(
            background,
            league,
            offset=(x_coord, bg_h - img_h - 300),  # Adjust the y-coordinate as needed
        )

        promotion_status = analyzer.league.promotion_status
        if promotion_status == PromotionStatus.NO_CHANGE:
            result_color = (255, 255, 255)
        elif promotion_status == PromotionStatus.PROMOTED:
            result_color = (220, 255, 220)
        elif promotion_status == PromotionStatus.DEMOTED:
            result_color = (255, 220, 220)

        result_text = f"Placed #{analyzer.league.placement}"
        x_spacing = background.size[0] // (self.clan_count + 1)
        x_coord = x_spacing * (clan_index + 1)

        return self.write_text(
            background,
            result_text,
            size=14,
            offset=(x_coord, bg_h - img_h - 500),  # Adjust the y-coordinate as needed
            fill=result_color,
        )

    def __write_clan_name(self, background: Image, analyzer: CwlAnalyzer, clan_index: int):
        x_spacing = background.size[0] // (self.clan_count + 1)
        x_coord = x_spacing * (clan_index + 1)

        return self.write_text(
            background,
            analyzer.league.clan_info["name"],
            offset=(x_coord, -180),  # Adjust the y-coordinate as needed
            size=18,
        )

    def __overlay_badge(self, background: Image, badge: Image, clan_index: int):
        bg_w, bg_h = background.size
        img_w, img_h = badge.size
        badge = badge.resize((int(img_w * 0.5), int(img_h * 0.5)))
        img_w, img_h = badge.size

        x_spacing = bg_w // (self.clan_count + 1)  # Calculate the spacing between badges

        x_coord = x_spacing * (clan_index + 1)  # Calculate the x-coordinate for the current badge
        x_coord -= img_w // 2  # Adjust the coordinate to center the badge horizontally

        return ImageUtils.overlay_image(
            background,
            badge,
            offset=(x_coord, bg_h - img_h - 400),  # Adjust the y-coordinate as needed
        )

    def __overlay_results(self, background: Image, clan: str, clan_index: int):
        stars = Image.open(f"results/{self.month}/{clan}_stars.png")

        bg_w, bg_h = background.size

        size = 0.35
        img_w, img_h = stars.size
        stars = stars.resize((int(img_w * size), int(img_h * size)))
        img_w, img_h = stars.size

        x_spacing = bg_w // (self.clan_count + 1)
        x_coord = x_spacing * (clan_index + 1)
        x_coord -= img_w // 2

        background = ImageUtils.overlay_image(
            background,
            stars,
            offset=(x_coord, bg_h - img_h - 80),  # Adjust the x-coordinate and y-coordinate
        )

        return background

    @staticmethod
    def write_text(
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

        text_width, text_height = draw.textsize(text, font=font)
        text_x = offset[0] + (bg_w - text_width) // 2 - bg_w / 2  # Adjusted x-axis calculation
        text_y = offset[1] + (bg_h - offset[1] - text_height) // 2

        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

        return background
