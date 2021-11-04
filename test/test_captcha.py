from math import floor
from os import environ as env

import pytest
from qqqr.constants import QzoneAppid, QzoneProxy
from qqqr.up import UPLogin, User
from qqqr.up.captcha import Captcha, ScriptHelper
from qqqr.up.captcha.jigsaw import Jigsaw


@pytest.fixture(scope='module')
def captcha() -> None:
    login = UPLogin(QzoneAppid, QzoneProxy, User(env['TEST_UIN'], env['TEST_PASSWORD']))
    captcha = login.captcha((login.check()).session)
    captcha.prehandle(login.xlogin_url)
    yield captcha


@pytest.fixture(scope='module')
def shelper(captcha, iframe):
    shelper = ScriptHelper(captcha.appid, captcha.sid, 2)
    shelper.parseCaptchaConf(iframe)
    yield shelper


@pytest.fixture(scope='module')
def iframe(captcha):
    yield captcha.iframe()


class TestCaptcha:
    def test_iframe(self, iframe):
        assert iframe

    def test_windowconf(self, shelper):
        assert shelper.conf
        assert shelper.conf['nonce']
        assert shelper.conf['powCfg']

    def test_match_md5(self, captcha, shelper, iframe):
        ans, duration = captcha.matchMd5(iframe, shelper.conf['powCfg'])
        assert ans <= 3e5
        assert duration > 0

    def test_puzzle(self, captcha, shelper):
        rio = lambda url: captcha.session.get(
            url, headers=captcha.header, allow_redirects=False
        ).content
        j = Jigsaw(
            *[rio(shelper.cdn(i)) for i in range(3)],
            top=floor(int(shelper.conf['spt']))
        )
        assert j.width > 0

    def test_verify(self, captcha):
        r = captcha.verify()
        assert r['randstr']


@pytest.fixture(scope='class')
def vm(captcha, iframe):
    yield captcha.getTdx(iframe)


class TestVM:
    def testGetInfo(self, vm):
        assert (d := vm.getInfo())
        assert d['info']

    def testCollectData(self, vm):
        vm.setData({'clientType': 2})
        vm.setData({'coordinate': [10, 24, 0.4103]})
        vm.setData({
            'trycnt': 1,
            'refreshcnt': 0,
            'slideValue': Captcha.imitateDrag(230),
            'dragobj': 1
        })
        vm.setData({'ft': 'qf_7P_n_H'})
        assert (d := vm.getData())
        assert len(d) > 200

    def testGetCookie(self, vm):
        assert vm.getCookie()
