import logging

import requests
import urllib3
from bs4 import BeautifulSoup

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

        # regeneratingagent request
        url = self.base_url + "info/regeneratingagent"
        response = session.post(url, headers=self.headers, verify=False)
        _LOGGER.debug(f"{DOMAIN} - regeneratingagent response {response.text}")
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("span", class_="subMenuValue")
        keys = ['regeneratingagent_commissioning', 'regeneratingagent_maintenance', 'regeneratingagent_refill', 'regenerations_total', 'regenerations_maintenance']
        values = []
        for result in results:
            values.append(result.text.split(" ")[0])
        regeneratingagent_response = dict(zip(keys, values))
        
        # logout
        url = self.base_url + "users/logout"
        response = session.get(url, verify=False)

        merged_response = data_response | signal_response | regeneratingagent_response
        _LOGGER.debug(f"{DOMAIN} - merged_response {merged_response}")
        return merged_response

    def get_warnings(self) -> dict:
        # create a session with login page
        url = self.base_url + "users/login"
        session = requests.Session()
        response = session.get(url, verify=False)

        # login with password
        url = self.base_url + "users/login"
        data = {"_method": "POST", "STLoginPWField": self.code, "function": "save"}
        response = session.post(url, headers=self.headers, data=data, verify=False)
        _LOGGER.debug(f"{DOMAIN} - login response {response.text}")

        # warnings request
        url = self.base_url + "home/warnings"
        response = session.post(url, headers=self.headers, verify=False)
        _LOGGER.debug(f"{DOMAIN} - warnings response {response.text}")
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("div", class_="notification")
        warnings_response = {}
        for result in results:
            divs = result.find("div", class_="notificationLeftText").find_all("div")
            warnings_response[result['id']] = divs[0].text+" "+divs[1].text
            
        # logout
        url = self.base_url + "users/logout"
        response = session.get(url, verify=False)

        return warnings_response    
        
    def get_holiday_mode(self) -> bool:
        # create a session with login page
        url = self.base_url + "users/login"
        session = requests.Session()
        response = session.get(url, verify=False)

        # login with password
        url = self.base_url + "users/login"
        data = {"_method": "POST", "STLoginPWField": self.code, "function": "save"}
        response = session.post(url, headers=self.headers, data=data, verify=False)
        _LOGGER.debug(f"{DOMAIN} - login response {response.text}")

        # holidaymode request
        url = self.base_url + "functions/holidaymode"
        response = session.post(url, headers=self.headers, verify=False)
        _LOGGER.debug(f"{DOMAIN} - holidaymode response {response.text}")
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find(id="changeHolidaymode")
        holidayMode = False
        if results.has_attr('checked'):
            holidayMode = True
                
        # logout
        url = self.base_url + "users/logout"
        response = session.get(url, verify=False)

        return holidayMode    
        
    # Extra Regeneration auslösen --> 482, 1
    # Extra Spülung auslösen --> 483, 1
    # Urlaubsmodus einschalten --> 484, 1
    # Urlaubsmodus ausschalten --> 484, 0
    def save_value(self, id: int, value: int) -> bool:
        # create a session with login page
        url = self.base_url + "users/login"
        session = requests.Session()
        response = session.get(url, verify=False)

        # login with password
        url = self.base_url + "users/login"
        data = {"_method": "POST", "STLoginPWField": self.code, "function": "save"}
        response = session.post(url, headers=self.headers, data=data, verify=False)
        _LOGGER.debug(f"{DOMAIN} - login response {response.text}")

        # set value for given id
        url = self.base_url + "keyboard/saveValue"
        data = {"_method": "POST", "ID": id, "Value": value}
        response = session.post(url, headers=self.headers, data=data, verify=False)
        _LOGGER.debug(f"{DOMAIN} - saveValue response {response.text}")
        success = False
        if (response.status_code == requests.codes.ok):
            success = True   
        
        # logout
        url = self.base_url + "users/logout"
        response = session.get(url, verify=False)
        
        return success
