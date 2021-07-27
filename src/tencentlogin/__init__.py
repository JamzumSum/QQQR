from dataclasses import dataclass

from requests import Session

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


class LoginBase:
    def __init__(self, app: APPID, proxy: Proxy, info: PT_QR_APP = None) -> None:
        self.session = Session()
        self.app = app
        self.proxy = proxy
        self.info = info if info else PT_QR_APP()
        self.header = {'DNT': '1', 'Referer': 'https://i.qq.com/', 'User-Agent': UA}


class TencentLoginError(RuntimeError):
    def __init__(self, code: int, msg: str, *args: object) -> None:
        self.code = code
        self.msg = msg
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Code {self.code}: {self.msg}"
