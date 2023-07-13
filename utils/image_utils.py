from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont


class ImageUtils:
    @staticmethod
    def get_image_from_url(url: str) -> Image:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))

    @staticmethod
    def overlay_image(background: Image, overlay: Image, offset: tuple[int] = (0, 0)):
        background.paste(overlay, offset, overlay)
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
