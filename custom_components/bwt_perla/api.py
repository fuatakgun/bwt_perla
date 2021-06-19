import logging

import requests
import urllib3

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0",
}

urllib3.disable_warnings()


class BWTPerlaApi:
    def __init__(self, host: str, code: str) -> None:
        self.host = host
        self.code = code
        self.base_url = "https://" + self.host + "/"
        self.headers = HEADERS
        self.headers["Host"] = self.host
        self.headers["Origin"] = self.base_url

    def get_data(self) -> dict:
        # create a session with login page
        url = self.base_url + "users/login"
        session = requests.Session()
        response = session.get(url, verify=False)

        # login with password
        url = self.base_url + "users/login"
        data = {"_method": "POST", "STLoginPWField": self.code, "function": "save"}
        response = session.post(url, headers=self.headers, data=data, verify=False)
        _LOGGER.debug(f"{DOMAIN} - login response {response.text}")

        # actualize data request
        url = self.base_url + "home/actualizedata"
        response = session.post(url, headers=self.headers, verify=False)
        _LOGGER.debug(f"{DOMAIN} - actualizedata response {response.text}")
        data_response: dict = response.json()

        # actualize signals request
        url = self.base_url + "home/actualizesignals"
        response = session.post(url, headers=self.headers, verify=False)
        _LOGGER.debug(f"{DOMAIN} - actualizesignals response {response.text}")
        signal_response: dict = response.json()

        # logout
        url = self.base_url + "users/logout"
        response = session.get(url, verify=False)

        merged_response = data_response | signal_response
        _LOGGER.debug(f"{DOMAIN} - merged_response {merged_response}")
        return merged_response
