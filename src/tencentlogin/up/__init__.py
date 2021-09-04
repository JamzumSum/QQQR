import re
from random import choice, random
from time import time_ns

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


@dataclass
class CheckResult:
    code: int
    verifycode: str
    salt: str
    verifysession: str
    isRandSalt: int
    ptdrvs: str
    session: str

    def __post_init__(self):
        self.code = int(self.code)
        self.isRandSalt = int(self.isRandSalt)
        salt = self.salt.split('\\x')[1:]
        salt = [chr(int(i, 16)) for i in salt]
        self.salt = ''.join(salt)


class UPLogin(LoginBase):
    node = 'node'
    _captcha = None

    def __init__(
        self, app: APPID, proxy: Proxy, user: User, info: PT_QR_APP = None
    ) -> None:
        super().__init__(app, proxy, info=info)
        assert user.uin
        assert user.pwd
        self.user = user

    def encodePwd(self, r: CheckResult) -> str:
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

        return self.getEncryption(self.user.pwd, r.salt, r.verifycode).strip()

    def check(self):
        """[summary]
            

        Raises:
            HTTPError: [description]

        Returns:
            dict: 
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
        return CheckResult(*r)

    def login(self, r: CheckResult, all_cookie=False, pastcode: int = 0):

        if r.code == StatusCode.Authenticated:
            # OK
            pass
        elif r.code == StatusCode.NeedCaptcha and pastcode == 0:
            # 0 -> 1: OK; !0 -> 1: Error
            self.login(self.passVC(r), all_cookie, StatusCode.NeedCaptcha)
        elif r.code == StatusCode.NeedVerify and pastcode != StatusCode.NeedVerify:
            # !10009 -> 10009: OK; 10009 -> 10009: Error
            raise NotImplementedError('wait for next version :D')
        else:
            raise TencentLoginError(r.code, str(r))

        data = {
            'u': self.user.uin,
            'p': self.encodePwd(r),
            'verifycode': r.verifycode,
            'pt_vcode_v1': 1 if pastcode == StatusCode.NeedCaptcha else 0,
            'pt_verifysession_v1': r.verifysession,
            'pt_randsalt': r.isRandSalt,
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
            'ptdrvs': r.ptdrvs,
            'sid': r.session,
        }
        self.header['Referer'] = 'https://xui.ptlogin2.qq.com/'
        response = self.session.get(LOGIN_URL, params=data, headers=self.header)
        if response.status_code != 200: raise HTTPError(response=response)

        r = re.findall(r"'(.*?)'[,\)]", response.text)
        r[0] = int(r[0])

        if r[0] != StatusCode.Authenticated:
            raise TencentLoginError(r[0], r[4])

        response = self.session.get(r[2], allow_redirects=False, headers=self.header)
        if all_cookie:
            r: dict = response.cookies.get_dict()
        else:
            r: str = response.cookies['p_skey']
        return r

    def captcha(self, sid: str):
        if not self._captcha:
            from .captcha import Captcha
            self._captcha = Captcha(self.session, self.app.appid, sid, self.header)
        return self._captcha

    def passVC(self, r: CheckResult):
        c = self.captcha(r.session)
        c.prehandle(self.xlogin_url)
        d = c.verify()
        r.code = int(d['errorCode'])
        r.verifycode = d['randstr']
        r.verifysession = d['ticket']
        return r
