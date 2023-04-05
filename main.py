import csv
import logging
import os
from datetime import datetime

from utils.cwl_analyzer import CwlAnalyzer
from utils.results_generator import PromotionStatus, ResultsGenerator

logger = logging.getLogger("analyzer")


def __main__():
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    month = datetime.now().strftime("%b").upper()
    os.makedirs(f"results/{month}", exist_ok=True)

    clan_map = {
        # "fever": "#2QYR2QJUP",
        "scrubs": "#2QR0CGUUL",
        # "tbc": "#2PRG8V0G2",
        # "bc": "#PJ2UVURC",
        # "bob": "#P8P0JCRC",
        # "ftc": "#2G0RR8VPU",
    }
    name_map = {
        "fever": "Cabin Fever",
        "scrubs": "Cabin Scrubs",
        "tbc": "TBC",
        "bc": "The Black Cabin",
        "bob": "BandofBrothers",
        "ftc": "FEAR THE CABIN",
    }
    promotion_map = {
        "fever": PromotionStatus.PROMOTED,
        "scrubs": PromotionStatus.PROMOTED,
        "tbc": PromotionStatus.PROMOTED,
        "bc": PromotionStatus.NO_CHANGE,
        "bob": PromotionStatus.NO_CHANGE,
        "ftc": PromotionStatus.NO_CHANGE,
    }
    # clan_map = {clan: tag for clan, tag in clan_map.items() if clan == "scrubs"}

    for clan, tag in clan_map.items():
        CwlAnalyzer().analyze(tag, clan, name_map[clan], month)
        ResultsGenerator(month, clan, tag, name_map[clan], promotion_map[clan]).generate()


if __name__ == "__main__":
    __main__()
