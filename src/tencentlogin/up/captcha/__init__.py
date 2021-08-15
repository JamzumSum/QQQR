import base64
import json
import re
from math import floor
from random import random
from time import time
from urllib.parse import urlencode

from jssupport.execjs import ExecJS
from jssupport.jsjson import json_loads
from requests import Session
from requests.exceptions import HTTPError
from tencentlogin.up.captcha.jigsaw import Jigsaw

PREHANDLE_URL = "https://t.captcha.qq.com/cap_union_prehandle"
SHOW_NEW_URL = "https://t.captcha.qq.com/cap_union_new_show"
VERIFY_URL = "https://t.captcha.qq.com/cap_union_new_verify"

time_s = lambda: int(1e3 * time())
rnd6 = lambda: str(random())[2:8]


def hex_add(h: str, o: int):
    return hex(int(h, 16) + o)[2:]


class ScriptHelper:
    def __init__(self, appid: int, sid: str, subsid: int) -> None:
        self.aid = appid
        self.sid = sid
        self.subsid = subsid

    def parseCaptchaConf(self, iframe: str):
        ijson = re.search(r"window\.captchaConfig=(\{.*\});", iframe).group(1)
        self.conf = json_loads(ijson)

    def cdn(self, cdn) -> str:
        assert cdn in (0, 1, 2)
        data = {
            'aid': self.aid,
            'sess': self.conf['sess'],
            'sid': self.sid,
            'subsid': self.subsid + cdn,
        }
        if cdn: data['img_index'] = cdn
        path = self.conf[f'cdnPic{cdn if cdn else 1}']
        return f"https://t.captcha.qq.com{path}?{urlencode(data)}"

    @staticmethod
    def slide_js_url(iframe):
        return re.search(
            r"https://captcha\.gtimg\.com/1/tcaptcha-slide\.\w+\.js", iframe
        ).group(0)

    @staticmethod
    def tdx_js_url(iframe):
        return "https://t.captcha.qq.com" + re.search(r'src="(/tdx.js.*?)"',
                                                      iframe).group(1)


class VM:
    vmAvailable = 0
    vmByteCode = 0
    window = "var window=new Proxy({}, {get: (targ, name) => {if (targ[name] !== undefined) return targ[name]; else if (name == 'window') return window; else return global[name]}});"

    def __init__(self, tdx: str) -> None:
        self.tdx = ExecJS(js=self.window + tdx)

    def getData(self):
        # return self.tdx('window.TDC.getData')
        return ""

    def getInfo(self):
        return json_loads(self.tdx('window.TDC.getInfo'))

    def setData(self, d: dict):
        return self.tdx('window.TDC.setData', d)

    def clearTc(self):
        return self.tdx('window.TDC.clearTc')


class Captcha:
    sess = None
    createIframeStart = 0
    subsid = 1

    # (c_login_2.js)showNewVC-->prehandle
    # prehandle(recall)--call tcapcha-frame.*.js-->new_show
    # new_show(html)--js in html->loadImg(url)
    def __init__(
        self, session: Session, appid: int, sid: str, header: dict = None
    ) -> None:
        self.session = session
        self.appid = appid
        self.sid = sid

        assert 'User-Agent' in header
        header['Referer'] = 'https://xui.ptlogin2.qq.com/'
        self.header = header

    @property
    def base64_ua(self):
        return base64.b64encode(self.header['User-Agent'].encode()).decode()

    def prehandle(self, xlogin_url):
        """
        call this before call `show`.

        args:
            xlogin_url: the url requested in QRLogin.request

        returns:
            dict

        example:
        ~~~
            {
                "state": 1,
                "ticket": "",
                "capclass": "1",
                "subcapclass": "15",
                "src_1": "cap_union_new_show",
                "src_2": "template/new_placeholder.html",
                "src_3": "template/new_slide_placeholder.html",
                "sess": "s0FXwryrkuYcdadBBb1d3_xihwN-42KXNAQQg6_5FKAuF-MdGmSlD9H7hQg29GLnk7uQLrsgHVRCQ7Mu1ylB6jY-XqrWaGPmoUfNJfJKjTY0ahaC16M6qb8bBsKJH67j8UPnI3r84TI35HMgtKh_t40jkHbp1l67l55rKEm4HHA27oIiEvD1rtUvb8UK2Rgfe7mb4wtuAvMrG-wVpZkamFhvx0e0GHlVCeDwBQ7o7cn0h4oH1V9pLN6GBkGiqBgHeTdFKqJH-FqNI*",
                "randstr": "",
                "sid": "874820883465668800"
            }
        ~~~
        """
        CALLBACK = '_aq_596882'
        data = {
            'aid': self.appid,
            'protocol': 'https',
            'accver': 1,
            'showtype': 'embed',
            'ua': self.base64_ua,
            'noheader': 1,
            'fb': 1,
            'enableDarkMode': 0,
            'sid': self.sid,
            'grayscale': 1,
            'clientype': 2,
            'cap_cd': "",
            'uid': "",
            'wxLang': "",
            'lang': 'zh-CN',
            'entry_url': xlogin_url,
            # 'js': '/tcaptcha-frame.a75be429.js'
            'subsid': self.subsid,
            'callback': CALLBACK,
            'sess': '',
        }
        self.createIframeStart = time_s()
        r = self.session.get(PREHANDLE_URL, params=data, headers=self.header)
        if r.status_code != 200:
            raise HTTPError(response=r)

        r = re.search(CALLBACK + r"\((\{.*\})\)", r.text).group(1)
        r = json.loads(r)
        self.sess = r['sess']
        self.subsid = 2
        return r

    def iframe(self):
        assert self.sess, 'call prehandle first'

        data = {
            'aid': self.appid,
            'protocol': 'https',
            'accver': 1,
            'showtype': 'embed',
            'ua': self.base64_ua,
            'noheader': 1,
            'fb': 1,
            'enableDarkMode': 0,
            'sid': self.sid,
            'grayscale': 1,
            'clientype': 2,
            'sess': self.sess,
            'fwidth': 0,
            'wxLang': '',
            'tcScale': 1,
            'uid': "",
            'cap_cd': "",
            'subsid': self.subsid,
            'rnd': rnd6(),
            'prehandleLoadTime': time_s() - self.createIframeStart,
            'createIframeStart': self.createIframeStart,
        }
        r = self.session.get(SHOW_NEW_URL, params=data, headers=self.header)
        self.header['Referer'] = r.request.url
        return r.text

    def getBlob(self, iframe: str):
        js_url = ScriptHelper.slide_js_url(iframe)
        js = self.session.get(js_url, headers=self.header).text
        return re.search(r"'(!function.*;')", js).group(1)

    def getTdx(self, iframe: str):
        js_url = ScriptHelper.tdx_js_url(iframe)
        self.vm = VM(self.session.get(js_url, headers=self.header).text)

    def matchMd5(self, iframe: str, powCfg: dict):
        if not hasattr(self, '_matchMd5'):
            blob = self.getBlob(iframe)
            blob = re.search(r",(function\(\w,\w,\w\).*?duration.*?),", blob).group(1)
            blob = f"var n=Object();!{blob}(null,n,null);"
            blob += "function matchMd5(p, m){return n.getWorkloadResult({nonce:p,target:m})}"
            self._matchMd5 = ExecJS(js=blob).bind('matchMd5')
        d = self._matchMd5(powCfg['prefix'], powCfg['md5'])
        d = json_loads(d.strip('\n'))
        return d['ans'], d['duration']

    def verify(self):
        """
        example:
        ~~~
        {
            "errorCode": "0",
            "randstr": "@VTn",
            "ticket": "t03UtRJOy9txaidDDdx5FBzSN_uwipfzMGe1pjDMIoO3dS2UUp1EEWiuZmIotD_709cAYhPGWo2M-uQZxorFH8JtGEhqpSYeRQ1h84opX2TQYWGRFATffLj8vsw_U3YJPHR5MPcvHsVGtM*",
            "errMessage": "",
            "sess": ""
        }
        ~~~
        """
        s = ScriptHelper(self.appid, self.sid, self.subsid)
        s.parseCaptchaConf(iframe := self.iframe())
        Ians, duration = self.matchMd5(iframe, s.conf['powCfg'])
        self.getTdx(iframe)

        rio = lambda url: self.session.get(url, headers=self.header).content
        j = Jigsaw(
            rio(s.cdn(0)), rio(s.cdn(1)), rio(s.cdn(2)), floor(int(s.conf['spt']))
        )

        # TODO: setData

        data = {
            'aid': self.appid,
            'protocol': 'https',
            'accver': 1,
            'showtype': s.conf['showtype'],
            'ua': self.base64_ua,
            'noheader': s.conf['noheader'],
            'fb': 1,
            'enableDarkMode': 0,
            'sid': self.sid,
            'grayscale': 1,
            'clientype': 2,
            'sess': s.conf['sess'],
            'fwidth': 0,
            'wxLang': "",
            'tcScale': 1,
            'uid': s.conf['uid'],
            'cap_cd': "",
            'rnd': rnd6(),
            'prehandleLoadTime': time_s() - self.createIframeStart,
            'createIframeStart': self.createIframeStart,
            'subsid': self.subsid,
            'cdata': 0,
            'vsig': s.conf['vsig'],
            'websig': s.conf['websig'],
            'subcapclass': s.conf['subcapclass'],
            'fpinfo': '',
            'ans': f'{j.left},{j.top};',
            'nonce': s.conf['nonce'],
            'vlg': f'{self.vm.vmAvailable}_{self.vm.vmByteCode}_1',
            'pow_answer': hex_add(s.conf['powCfg']['prefix'], Ians) if Ians else Ians,
            'pow_calc_time': duration,
            'eks': self.vm.getInfo()['info'],
            'tlg': len(collect := self.vm.getData()),
            s.conf['collectdata']: collect,
            # TODO: unknown
            # 'vData': 'gC*KM-*rjuHBcUjIt9kL6SV6JGdgfzMmP0BiFcaDg_7ctHwCjeoz4quIjb2FTgdJLBeCcKCZB_Mv7suXumolfmpSKZVIp7Un2N3b*fbwHX9aqRgjp5fmsgkf6aOgnhU_ttr_4xJZKVjStGX*hMwgBeHE_zuz-iDKy1coGdurLh559T6MoBdJdMAxtIlGJxAexbt6eDz3Aw5pD_tR01ElO7YY',
        }
        r = self.session.post(VERIFY_URL, data=data, headers=self.header)

        self.sess = None
        self.createIframeStart = 0
        r = r.json()
        if int(r['errorCode']):
            raise RuntimeError(f"Code {r['errorCode']}: {r['errMessage']}")
        return r
