import re
from dataclasses import dataclass
from random import random
from time import sleep
from typing import Dict, Union

import requests
from requests.exceptions import HTTPError

SHOW_QR = 'https://ssl.ptlogin2.qq.com/ptqrshow'
XLOGIN_URL = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin'
POLL_QR = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
LOGIN_URL = 'https://ptlogin2.qzone.qq.com/check_sig'

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70"


@dataclass(frozen=True)
class PT_QR_APP:
    app: str = ""
    link: str = ""
    register: str = ""
    help: str = ""


@dataclass(frozen=True)
class Proxy:
    proxy_url: str
    s_url: str


@dataclass(frozen=True)
class APPID:
    appid: int
    daid: int


class TencentQR:
    def __init__(self, app: APPID, proxy: Proxy, info: PT_QR_APP = None) -> None:
        self.session = requests.Session()
        self.app = app
        self.proxy = proxy
        self.info = info if info else PT_QR_APP()
        self.header = {'DNT': '1', 'Referer': 'https://i.qq.com/', 'User-Agent': UA}

    def request(self):
        data = {
            'hide_title_bar': 1,
            'style': 22,
            "daid": self.app.daid,
            "low_login": 0,
            "qlogin_auto_login": 1,
            'no_verifyimg': 1,
            'link_target': 'blank',
            'appid': self.app.appid,
            'target': 'self',
            's_url': self.proxy.s_url,
            'proxy_url': self.proxy.proxy_url,
            'pt_qr_app': self.info.app,
            'pt_qr_link': self.info.link,
            'self_regurl': self.info.register,
            'pt_qr_help_link': self.info.help,
            'pt_no_auth': 1,
        }
        r = self.session.get(XLOGIN_URL, params=data, headers=self.header)
        if r.status_code != 200: raise HTTPError(response=r)

        self.local_token = int(r.cookies['pt_local_token'])
        return self

    def show(self):
        data = {
            'appid': self.app.appid,
            'e': 2,
            'l': 'M',
            's': 3,
            'd': 72,
            'v': 4,
            't': random(),
            'daid': self.app.daid,
            'pt_3rd_aid': 0,
        }
        r = self.session.get(SHOW_QR, params=data, headers=self.header)
        if r.status_code != 200: raise HTTPError(response=r)

        self.qrsig = r.cookies['qrsig']
        return r.content

    def encodedSig(self):
        # str.hash33
        phash = 0
        for c in self.qrsig:
            phash += (phash << 5) + ord(c)
        return 0x7fffffff & phash

    def pollStat(self):
        """poll status of the qr

        Raises:
            HTTPError: if response code != 200

        Returns:
            list: (code, ?, url, ?, msg, my_name)
        """
        data = {
            'u1': self.proxy.s_url,
            'ptqrtoken': self.encodedSig(),
            'ptredirect': 0,
            'h': 1,
            't': 1,
            'g': 1,
            'from_ui': 1,
            'ptlang': 2052,
            # 'action': 3-2-1626611307380,
            # 'js_ver': 21071516,
            'js_type': 1,
            'login_sig': "",
            'pt_uistyle': 40,
            'aid': self.app.appid,
            'daid': self.app.daid,
            # 'ptdrvs': 'JIkvP2N0eJUzU3Owd7jOvAkvMctuVfODUMSPltXYZwCLh8aJ2y2hdSyFLGxMaH1U',
            # 'sid': 6703626068650368611,
            'has_onekey': 1,
        }
        r = self.session.get(POLL_QR, params=data, headers=self.header)
        if r.status_code != 200: raise HTTPError(response=r)

        r = re.findall(r"'(.*?)'[,\)]", r.text)
        r[0] = int(r[0])
        if r[0] == 0: self.login_url = r[2]
        return r

    def login(self, all_cookie=False) -> Union[Dict, str]:
        r = self.session.get(self.login_url, allow_redirects=False)
        if r.status_code != 302: raise HTTPError(response=r)
        if all_cookie:
            return r.cookies.get_dict()
        else:
            return r.cookies['p_skey']

    def loop(self, refresh_time=6, polling_freq=3, all_cookie=False):
        from .constants import StatusCode
        i = -1
        r = [StatusCode.Expired]
        while True:
            if r[0] == StatusCode.Expired:
                # expired
                i += 1
                if i > refresh_time: raise TimeoutError
                yield self.show()
            elif r[0] == StatusCode.Authenticated:
                # login success
                yield self.login(all_cookie)
                return
            else:
                if r[0] not in [StatusCode.Waiting, StatusCode.Scanned]:
                    print(f"Code {r[0]}: {r[4]}")  # show msg
            sleep(polling_freq)
            r = self.pollStat()
