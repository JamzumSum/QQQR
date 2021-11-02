import re
from random import random
from typing import Union

from ..base import LoginBase
from ..encrypt import hash33
from ..type import APPID, PT_QR_APP, Proxy

ST_PORT = [4301, 4303, 4305, 4307, 4309]
GET_UIN_URL = "https://localhost.ptlogin2.qq.com:{port}/pt_get_uins"
GET_ST_URL = "https://localhost.ptlogin2.qq.com:{port}/pt_get_st"
JUMP_URL = "https://ssl.ptlogin2.qq.com/jump"


class LCLogin(LoginBase):
    def __init__(
        self, app: APPID, proxy: Proxy, uin: int, info: PT_QR_APP = None
    ) -> None:
        super().__init__(app, proxy, info=info)
        self.uin = uin
        self.header['Referer'] = "https://xui.ptlogin2.qq.com/"

    def checkLoginList(self):
        """Check if current uin is logined

        Raises:
            RuntimeError: if no qq client answered
        """
        if not hasattr(self, 'local_token'):
            self.local_token = random()
        query = {
            'callback': 'ptui_getuins_CB',
            'r': random(),
            'pt_local_tk': self.local_token
        }
        for p in ST_PORT:
            r = self.session.get(
                GET_UIN_URL.format(port=p),
                params=query,
                headers=self.header,
                cookies={'pt_local_token': str(self.local_token)}
            )
            if r.status_code == 200:
                self.port = p
                uins = re.findall(r'"uin":(\d+)', r.text)
                assert any(int(i) == self.uin for i in uins)
                return
        raise RuntimeError

    def getClientKey(self):
        data = {
            'clientuin': self.uin,
            'r': random(),
            'pt_local_tk': self.local_token,
            'callback': '__jp0'
        }
        response = self.session.get(
            GET_ST_URL.format(port=self.port), params=data, headers=self.header
        )
        if response.status_code == 200:
            return self.session.cookies['clientkey']

    def login(self) -> dict[str, str]:
        data = {
            'clientuin': self.uin,
            'keyindex': 9,
            'pt_aid': self.app.appid,
            'daid': self.app.daid,
            'u1': self.proxy.s_url,
            'pt_local_tk': hash33(self.getClientKey()),
            'pt_3rd_aid': 0,
            'ptopt': 1,
            'style': 40,
        }
        response = self.session.get(JUMP_URL, params=data, headers=self.header)
        # ptui_qlogin_CB('0', 'https://ptlogin2.qzone.qq.com/check_sig?pttype=2&uin=458973857&service=jump&nodirect=0&ptsigx=8bf2db705c2606074ba50cc8c1678050bf481d5158abd97b9f001a33ae8f6dc06aa0bb48bf7f531bba13373cb05fd70005c739e01aa85efffd6d44b01cd38f7c&s_url=https%3A%2F%2Fqzs.qzone.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&f_url=&ptlang=2052&ptredirect=100&aid=1000101&daid=5&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=2&pt_aid=549000912&pt_aaid=0&pt_light=0&pt_3rd_aid=0', '')
        r = re.findall(r"'(.*?)'[,\)]", response.text)

        response = self.session.get(r[1], headers=self.header)
        response.raise_for_status()

        return self.session.cookies.get_dict()
