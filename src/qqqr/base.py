from abc import ABC, abstractmethod
from ssl import create_default_context
from urllib.parse import urlencode

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

from .type import APPID, PT_QR_APP, Proxy

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52"
CIPHERS = [
    "ECDHE+AESGCM",
    "ECDHE+CHACHA20",
    "DHE+AESGCM",
    "DHE+CHACHA20",
    "ECDH+AESGCM",
    "DH+AESGCM",
    "RSA+AESGCM",
    "!aNULL",
    "!eNULL",
    "!MD5",
    "!DSS",
]
XLOGIN_URL = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin'


class TLSAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        """
        A TransportAdapter that re-enables 3DES support in Requests.
        """
        self.CIPHERS = ':'.join(CIPHERS)
        super().__init__(*args, **kwargs)

    def __context(self):
        c = create_default_context()
        c.set_ciphers(self.CIPHERS)
        return c

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.__context()
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.__context()
        return super(TLSAdapter, self).proxy_manager_for(*args, **kwargs)


class LoginBase(ABC):
    def __init__(self, app: APPID, proxy: Proxy, info: PT_QR_APP = None) -> None:
        self.session = Session()
        self.session.mount('https://', TLSAdapter())
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

    @abstractmethod
    def login(self, *args, **kwds) -> dict[str, str]:
        return

    # def ja3Detect(self) -> dict:
    #     # for debuging
    #     return self.session.get('https://ja3er.com/json', headers=self.header).json()
