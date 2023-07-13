import csv
import logging
import os
from datetime import datetime

from utils.cwl_analyzer import CwlAnalyzer
from utils.overview_generator import OverviewGenerator
from utils.results_generator import ResultsGenerator

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
        "bc": "#PJ2UVURC",
        "tbc": "#2PRG8V0G2",
        "fever": "#2QYR2QJUP",
        "scrubs": "#2QR0CGUUL",
        # "bob": "#P8P0JCRC",
        # "ftc": "#2G0RR8VPU",
        "couch": "#2LGP929CP",
        "ls": "#GCCUC2YR",
    }
    recheck = False
    name_map = {
        "bc": "The Black Cabin",
        "tbc": "TBC",
        "fever": "Cabin Fever",
        "scrubs": "Cabin Scrubs",
        "bob": "BandofBrothers",
        "ftc": "FEAR THE CABIN",
        "couch": "Cabin Couch",
        "ls": "Love Story",
    }

    all_clans = {}
    for clan, tag in clan_map.items():
        analyzer = CwlAnalyzer(recheck=recheck)
        analyzer.analyze(tag, clan, name_map[clan], month)
        ResultsGenerator(month, clan, tag, name_map[clan], analyzer).generate()

        all_clans[clan] = analyzer

    OverviewGenerator(month, all_clans).generate()


if __name__ == "__main__":
    __main__()
