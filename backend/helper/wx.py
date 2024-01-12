import os
import logging
import requests

import config as CONFIG

class WXObject():
    def __init__(self, code):
        self.code = code
        self.app_id = os.environ.get("WX_APP_ID")
        self.secret = os.environ.get("WX_SECRET")
        self.access_token = ""
        self.openid = ""
        self.unionid = ""
        self.username = ""

    def _getAccessToken(self):
        access_token_url = f"{CONFIG.WX_ACCESS_TOKEN_URL}?appid={self.app_id}&secret={self.secret}&code={self.code}&grant_type=authorization_code"
        try:
            response = requests.get(access_token_url)
            if response.status_code == 200:
                json_data = response.json()
                self.access_token = json_data["access_token"]
                self.openid = json_data["openid"]
        except:
            logging.info(f"code {self.code} _getAccessToken is processing wrong")

    def _getUserinfo(self):
        user_info_url = f"{CONFIG.WX_USERINFO_URL}?openid={self.openid}&access_token={self.access_token}"
        try:
            response = requests.get(user_info_url)
            if response.status_code == 200:
                json_data = response.json()
                self.unionid = json_data["unionid"]
                self.username = json_data["nickname"]
        except:
            logging.info(f"code {self.code} _getUserinfo is processing wrong")
        

    def getUserInfo(self):
        self._getAccessToken()
        self._getUserinfo()
        return self.unionid, self.username