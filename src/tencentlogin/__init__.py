from dataclasses import dataclass
from urllib.parse import urlencode

from requests import Session
from requests.exceptions import HTTPError

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
XLOGIN_URL = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin'


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


class LoginBase:
    def __init__(self, app: APPID, proxy: Proxy, info: PT_QR_APP = None) -> None:
        self.session = Session()
        self.app = app
        self.proxy = proxy
        self.info = info if info else PT_QR_APP()
        self.header = {'DNT': '1', 'Referer': 'https://i.qq.com/', 'User-Agent': UA}

    @property
    def xlogin_url(self):
        return XLOGIN_URL + '?' + urlencode({
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
        })

    def request(self):
        r = self.session.get(self.xlogin_url, headers=self.header)
        if r.status_code != 200: raise HTTPError(response=r)

        self.local_token = int(r.cookies['pt_local_token'])
        return self


class TencentLoginError(RuntimeError):
    def __init__(self, code: int, msg: str, *args: object) -> None:
        self.code = code
        self.msg = msg
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Code {self.code}: {self.msg}"
