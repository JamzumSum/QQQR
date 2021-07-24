import re
from random import choice, random
from time import time_ns

from requests.exceptions import HTTPError

from .. import *

CHECK_URL = "https://ssl.ptlogin2.qq.com/check"
LOGIN_URL = 'https://ssl.ptlogin2.qq.com/login'
LOGIN_JS = 'https://qq-web.cdn-go.cn/any.ptlogin2.qq.com/v1.3.0/ptlogin/js/c_login_2.js'


@dataclass
class User:
    uin: int
    pwd: str


class UPLogin(LoginBase):
    def __init__(
        self, app: APPID, proxy: Proxy, user: User, info: PT_QR_APP = None
    ) -> None:
        super().__init__(app, proxy, info=info)
        self.user = user

    def encodePwd(self, r) -> str:
        if not hasattr(self, 'getEncryption'):
            js = self.session.get(LOGIN_JS).text
            funcs = re.search(
                r"function\(module,exports,__webpack_require__\).*\}", js
            ).group(0)
            js = "var navigator = new Object; navigator.appName = 'Netscape';"
            js += f"var a = [{funcs}];"
            js += "function n(k) { var t, e = new Object; return a[k](t, e, n), e }\n"
            js += "function getEncryption(p, s, v) { var t, e = new Object; return a[9](t, e, n), e['default'].getEncryption(p, s, v, undefined) }"

            import execjs
            from functools import partial
            js = execjs.compile(js)
            self.getEncryption = partial(js.call, 'getEncryption')
        salt = r[2].split('\\x')[1:]
        salt = [chr(int(i, 16)) for i in salt]
        salt = ''.join(salt)
        return self.getEncryption(self.user.pwd, salt, r[1])

    def check(self):
        """[summary]
            

        Raises:
            HTTPError: [description]

        Returns:
            list: (code, verifycode, salt, pt_verifysession_v1, isRandSalt, ptdrvs, sid)
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
        r = self.session.get(CHECK_URL, params=data)
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

    def login(self, r, all_cookie=False):
        assert r[0] == 0
        assert len(r) == 7

        data = {
            'u': self.user.uin,
            'p': self.encodePwd(r),
            'verifycode': r[1],
            'pt_vcode_v1': 0,
            'pt_verifysession_v1': r[3],
            'pt_randsalt': r[4],  # 2 or r[4]
            'u1': self.proxy.s_url,
            'ptredirect': 0,
            'h': 1,
            't': 1,
            'g': 1,
            'from_ui': 1,
            'ptlang': 2052,
            'action': f"2-{choice([1, 2])}-{int(time_ns() / 1e6)}",
            # 'js_ver': 21072114,
            'js_type': 1,
            'login_sig': self.session.cookies.get('pt_login_sig', default=''),
            'pt_uistyle': 40,
            'aid': self.app.appid,
            'daid': self.app.daid,
            'ptdrvs': r[5],
            'sid': r[6],
        }
        r = self.session.get(LOGIN_URL, params=data)
        if r.status_code != 200: raise HTTPError(response=r)

        r = re.findall(r"'(.*?)'[,\)]", r.text)
        if r[0] != '0': raise RuntimeError(f"Code {r[0]}: {r[4]}")

        login_url = r[2]
        r = self.session.get(login_url, allow_redirects=False)

        if all_cookie:
            return r.cookies.get_dict()
        else:
            return r.cookies['p_skey']
