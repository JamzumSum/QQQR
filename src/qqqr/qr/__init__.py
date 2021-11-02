import re
from random import random
from threading import Thread
from time import sleep
from typing import Callable

from requests.exceptions import HTTPError

from ..base import LoginBase
from ..constants import StatusCode
from ..encrypt import hash33
from ..exception import UserBreak

SHOW_QR = 'https://ssl.ptlogin2.qq.com/ptqrshow'
XLOGIN_URL = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin'
POLL_QR = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
LOGIN_URL = 'https://ptlogin2.qzone.qq.com/check_sig'

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70"


class QRLogin(LoginBase):
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
        r.raise_for_status()

        self.qrsig = r.cookies['qrsig']
        return r.content

    def pollStat(self):
        """poll status of the qr

        Raises:
            HTTPError: if response code != 200

        Returns:
            list: (code, ?, url, ?, msg, my_name)
        """
        data = {
            'u1': self.proxy.s_url,
            'ptqrtoken': hash33(self.qrsig),
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
        r.raise_for_status()

        r = re.findall(r"'(.*?)'[,\)]", r.text)
        r[0] = int(r[0])
        if r[0] == 0: self.login_url = r[2]
        return r

    def login(self) -> dict[str, str]:
        r = self.session.get(self.login_url, allow_redirects=False, headers=self.header)
        if r.status_code != 302: raise HTTPError(response=r)
        return r.cookies.get_dict()

    def loop(
        self,
        send_callback: Callable[[bytes], None],
        expire_callback: Callable[[bytes], None] = None,
        refresh_time: int = 6,
        polling_freq: float = 3,
    ):
        class Q(Thread):
            _INT = False

            def __init__(self):
                super().__init__(name='QR')

            def run(q):
                for i in range(refresh_time):
                    send = expire_callback if i else send_callback
                    send(self.show())
                    while True:
                        sleep(polling_freq)
                        if q._INT: raise UserBreak
                        stat = self.pollStat()
                        if stat[0] == StatusCode.Expired: break
                        if stat[0] == StatusCode.Authenticated:
                            q._result = self.login()
                            return
                raise TimeoutError

            def result(self, timeout: float = None) -> None:
                super().join(timeout=timeout)
                return self._result

            def stop(self):
                self._INT = True

        expire_callback = expire_callback or send_callback
        q = Q()
        q.start()
        return q
