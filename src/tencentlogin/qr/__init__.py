import logging
import re
from collections import defaultdict
from random import random
from typing import Callable, Dict, Union

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from requests.exceptions import HTTPError

from ..base import LoginBase
from ..constants import StatusCode
from ..encrypt import hash33

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
        if r.status_code != 200: raise HTTPError(response=r)

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
        if r.status_code != 200: raise HTTPError(response=r)

        r = re.findall(r"'(.*?)'[,\)]", r.text)
        r[0] = int(r[0])
        if r[0] == 0: self.login_url = r[2]
        return r

    def login(self, all_cookie=False) -> Union[Dict, str]:
        r = self.session.get(self.login_url, allow_redirects=False, headers=self.header)
        if r.status_code != 302: raise HTTPError(response=r)
        if all_cookie:
            return r.cookies.get_dict()
        else:
            return r.cookies['p_skey']

    def loop(self, refresh_time=6, polling_freq=3, all_cookie=False, block=True):
        that = self

        class WaitScan:
            def __init__(
                self, refresh_callback: Callable[[bytes], None],
                return_callback: Callable[[Union[dict, str]], None]
            ) -> None:

                self.sched = (BlockingScheduler if block else BackgroundScheduler)()
                self.job = self.sched.add_job(
                    self.once,
                    trigger='interval',
                    name='QRLogin.loop',
                    seconds=polling_freq,
                )
                self._refresh = refresh_callback
                self._return = return_callback
                self.cnt = 0

            def once(self):
                if self.cnt == 0:
                    self._refresh(that.show())
                    self.cnt += 1
                    return
                if refresh_time and self.cnt >= refresh_time:
                    self.exc = TimeoutError
                    self.job.remove()
                    self.stop()
                    return

                r = that.pollStat()
                return defaultdict(
                    lambda: \
                        lambda: r[0] in [StatusCode.Waiting, StatusCode.Scanned] or
                        print(f"Code {r[0]}: {r[4]}"),
                    {
                        StatusCode.Expired: lambda: \
                            self._refresh(that.show()) or self.__setattr__('cnt', self.cnt + 1),
                        StatusCode.Authenticated: lambda: \
                            self._return(self.job.remove() or that.login(all_cookie)) or self.stop(),
                    }
                )[r[0]]()

            def start(self):
                logger = logging.getLogger('apscheduler.executors.default')
                lv = logger.level
                logger.setLevel(logging.WARNING)
                self.sched.start()
                logger.setLevel(lv)
                if block and hasattr(self, 'exc'): raise self.exc

            def stop(self, exception=False):
                self.sched.shutdown()
                if exception: self.exc = KeyboardInterrupt

        return WaitScan
