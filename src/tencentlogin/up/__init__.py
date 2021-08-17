import re
from random import choice, random
from time import time_ns
from typing import Union

from requests.exceptions import HTTPError

from tencentlogin.constants import StatusCode

from .. import *
from jssupport.execjs import ExecJS

CHECK_URL = "https://ssl.ptlogin2.qq.com/check"
LOGIN_URL = 'https://ssl.ptlogin2.qq.com/login'
LOGIN_JS = 'https://qq-web.cdn-go.cn/any.ptlogin2.qq.com/v1.3.0/ptlogin/js/c_login_2.js'


@dataclass
class User:
    uin: int
    pwd: str


class UPLogin(LoginBase):
    node = 'node'
    _captcha = None

    def __init__(
        self, app: APPID, proxy: Proxy, user: User, info: PT_QR_APP = None
    ) -> None:
        super().__init__(app, proxy, info=info)
        self.user = user

    def encodePwd(self, r) -> str:
        assert self.user.pwd, 'password should not be empty'

        if not hasattr(self, 'getEncryption'):
            js = self.session.get(LOGIN_JS, headers=self.header).text
            funcs = re.search(
                r"function\(module,exports,__webpack_require__\).*\}", js
            ).group(0)
            js = "var navigator = new Object; navigator.appName = 'Netscape';"
            js += f"var a = [{funcs}];"
            js += "function n(k) { var t, e = new Object; return a[k](t, e, n), e }\n"
            js += "function getEncryption(p, s, v) { var t, e = new Object; return a[9](t, e, n), e['default'].getEncryption(p, s, v, undefined) }"

            js = ExecJS(self.node, js=js)
            self.getEncryption = js.bind('getEncryption')
        salt = r[2].split('\\x')[1:]
        salt = [chr(int(i, 16)) for i in salt]
        salt = ''.join(salt)
        return self.getEncryption(self.user.pwd, salt, r[1]).strip()

    def check(self):
        """[summary]
            

        Raises:
            HTTPError: [description]

        Returns:
            list: (check_return_code, verifycode, salt, pt_verifysession_v1, isRandSalt, ptdrvs, session_id)
                code = 0/2/3 hideVC; 
                code = 1 showVC
        """
        data = {
            'regmaster': '',
            'pt_tea': 2,
            'pt_vcode': 1,
            'uin': self.user.uin,
            'appid': self.app.appid,
            # 'js_ver': 21072114,
            'js_type': 1,
            'login_sig': self.session.cookies.get('pt_login_sig', default=''),
            'u1': self.proxy.s_url,
            'r': random(),
            'pt_uistyle': 40,
        }
        r = self.session.get(CHECK_URL, params=data, headers=self.header)
        if r.status_code != 200: raise HTTPError(response=r)

        r = re.findall(r"'(.*?)'[,\)]", r.text)
        r[0] = int(r[0])
        return r
        # (
        #     '0', '!JRV', '\x00\x00\x00\x00\x1b\x5b\x62\xa1',
        #     '9a0c40e8365dbabd1e864c9baf273ba5d3b53292224e02688f3f23f37f043d0c07d968d829a4b8b10f72061a7d2b05e0195a9814345353f3',
        #     '2', 'iycxH51-6f9oQSwVtu91*UgHRvqU9RDD7JTTLyRvj9FmMB7fcQrgAbWrKlYs3sx1',
        #     '331616062933615434'
        # )

    def login(self, r, all_cookie=False, pastcode: int = 0) -> Union[str, dict]:
        assert len(r) == 7

        if r[0] == StatusCode.Authenticated: pass
        elif r[0] == StatusCode.NeedCaptcha:
            if pastcode == 0:
                self.login(self.passVC(r), all_cookie, StatusCode.NeedCaptcha)
        elif r[0] == StatusCode.NeedVerify:
            if pastcode != StatusCode.NeedVerify:
                raise NotImplementedError('wait for next version :D')
        else:
            raise TencentLoginError(r[0], r[4])

        data = {
            'u': self.user.uin,
            'p': self.encodePwd(r),
            'verifycode': r[1],
            'pt_vcode_v1': 1 if pastcode == StatusCode.NeedCaptcha else 0,
            'pt_verifysession_v1': r[3],
            'pt_randsalt': r[4],  # 2 or r[4]
            'u1': self.proxy.s_url,
            'ptredirect': 0,
            'h': 1,
            't': 1,
            'g': 1,
            'from_ui': 1,
            'ptlang': 2052,
            'action': f"{3 if pastcode == StatusCode.NeedCaptcha else 2}-{choice([1, 2])}-{int(time_ns() / 1e6)}",
            # 'js_ver': 21072114,
            'js_type': 1,
            'login_sig': self.session.cookies.get('pt_login_sig', default=''),
            'pt_uistyle': 40,
            'aid': self.app.appid,
            'daid': self.app.daid,
            'ptdrvs': r[5],
            'sid': r[6],
        }
        self.header['Referer'] = 'https://xui.ptlogin2.qq.com/'
        response = self.session.get(LOGIN_URL, params=data, headers=self.header)
        if response.status_code != 200: raise HTTPError(response=response)

        r = re.findall(r"'(.*?)'[,\)]", response.text)
        r[0] = int(r[0])

        if r[0] != StatusCode.Authenticated:
            raise TencentLoginError(r[0], r[4])

        login_url = r[2]
        r = self.session.get(login_url, allow_redirects=False, headers=self.header)
        if all_cookie:
            return r.cookies.get_dict()
        else:
            return r.cookies['p_skey']

    def captcha(self, sid: str):
        if not self._captcha:
            from .captcha import Captcha
            self._captcha = Captcha(self.session, self.app.appid, sid, self.header)
        return self._captcha

    def passVC(self, r: list):
        c = self.captcha(r[6])
        c.prehandle(self.xlogin_url)
        d = c.verify()
        r[0] = 0
        r[1] = d['randstr']
        r[3] = d['ticket']
        return r
