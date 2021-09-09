from math import floor
from os import environ as env

import pytest
from tencentlogin.constants import QzoneAppid, QzoneProxy
from tencentlogin.up import UPLogin, User
from tencentlogin.up.captcha import Captcha, ScriptHelper
from tencentlogin.up.captcha.jigsaw import Jigsaw

captcha = xlogin_url = iframe = shelper = None


def setup_module() -> None:
    global captcha, xlogin_url, shelper
    login = UPLogin(QzoneAppid, QzoneProxy, User(env['TEST_UIN'], env['TEST_PASSWORD']))
    captcha = login.captcha(login.check().session)
    xlogin_url = login.xlogin_url
    captcha.prehandle(xlogin_url)
    shelper = ScriptHelper(captcha.appid, captcha.sid, 2)


# @pytest.mark.skipif(not captcha, reason='need login')
class TestCaptcha:
    def test_iframe(self):
        html = captcha.iframe()
        assert html
        global iframe
        iframe = html

    def test_windowconf(self):
        shelper.parseCaptchaConf(iframe)
        assert shelper.conf
        assert shelper.conf['nonce']
        assert shelper.conf['powCfg']

    def test_match_md5(self):
        ans, duration = captcha.matchMd5(iframe, shelper.conf['powCfg'])
        assert ans <= 3e5
        assert duration > 0

    def test_puzzle(self):
        rio = lambda url: captcha.session.get(
            url, headers=captcha.header, allow_redirects=False
        ).content
        j = Jigsaw(
            *[rio(shelper.cdn(i)) for i in range(3)],
            top=floor(int(shelper.conf['spt']))
        )
        assert j.width > 0

    def test_verify(self):
        r = captcha.verify()
        assert r['randstr']


# @pytest.mark.skipif(not iframe or not prehandled, reason='pred test failed')
class TestVM:
    @classmethod
    def setup_class(cls):
        cls.vm = captcha.getTdx(iframe)

    def testGetInfo(self):
        assert (d := self.vm.getInfo())
        assert d['info']

    def testCollectData(self):
        self.vm.setData({'clientType': 2})
        self.vm.setData({'coordinate': [10, 24, 0.4103]})
        self.vm.setData({
            'trycnt': 1,
            'refreshcnt': 0,
            'slideValue': Captcha.imitateDrag(230),
            'dragobj': 1
        })
        self.vm.setData({'ft': 'qf_7P_n_H'})
        assert (d := self.vm.getData())
        assert len(d) > 200

    def testGetCookie(self):
        assert self.vm.getCookie()
