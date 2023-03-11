import logging
import os
from urllib.parse import quote, urljoin

import requests
from dotenv import load_dotenv


class CocApiService:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("COC_API_TOKEN")
        self.base_url = os.getenv("COC_API_URL")
        self.logger = logging.getLogger("analyzer")

    def get_cwl_info(self, clan_tag: str) -> dict:
        url = urljoin(self.base_url, quote(f"clans/{clan_tag}/currentwar/leaguegroup"))
        return self.__send_get_request(url)

    def get_war_info(self, war_tag: str) -> dict:
        url = urljoin(self.base_url, quote(f"clanwarleagues/wars/{war_tag}"))
        return self.__send_get_request(url)

    def get_clan_info(self, clan_tag: str) -> dict:
        url = urljoin(self.base_url, quote(f"clans/{clan_tag}"))
        return self.__send_get_request(url)

    def __send_get_request(self, url: str) -> dict:
        self.logger.info(f"Calling coc api {url}")
        response = requests.get(url, headers=self.__get_auth_header())
        if response.status_code == 200:
            return response.json()

        raise Exception(f"Error calling coc api: {response.status_code} {response.text}")

    def __get_auth_header(self):
        return {"Authorization": f"Bearer {self.token}"}
