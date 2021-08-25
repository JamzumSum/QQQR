from math import floor
from unittest import TestCase

from tencentlogin.constants import QzoneAppid, QzoneProxy
from tencentlogin.up import UPLogin, User
from tencentlogin.up.captcha import Captcha, ScriptHelper
from tencentlogin.up.captcha.jigsaw import Jigsaw


class TestCaptcha(TestCase):
    def setUp(self) -> None:
        import yaml
        with open('config/user.yml') as f:
            self.q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))

    def testLogin(self):
        r = self.q.check()
        if r[0] == 1:
            html = self.q.passVC(r)
            self.assertTrue(html)
            with open('tmp/iframe.html', 'w', encoding='utf8') as f:
                f.write(html)


class TestScript(TestCase):
    def setUp(self) -> None:
        import yaml
        with open('config/user.yml') as f:
            q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))
            r = q.check()
            assert r[0] == 1
            self.c = q.captcha(r[6])
            self.c.prehandle(q.xlogin_url)

    def testConf(self):
        html = self.c.iframe()
        s = ScriptHelper(self.c.appid, self.c.sid, 2)
        s.parseCaptchaConf(html)
        self.assertTrue(s.conf)
        self.assertTrue(s.conf['nonce'])
        self.assertTrue(s.conf['powCfg'])

    def testMatchMd5(self):
        html = self.c.iframe()
        html = self.c.iframe()
        s = ScriptHelper(self.c.appid, self.c.sid, 2)
        s.parseCaptchaConf(html)
        ans, duration = self.c.matchMd5(html, s.conf['powCfg'])
        self.assertLessEqual(ans, 3e5)
        self.assertGreater(duration, 0)

    def testCdn(self):
        html = self.c.iframe()
        html = self.c.iframe()
        s = ScriptHelper(self.c.appid, self.c.sid, 2)
        s.parseCaptchaConf(html)
        rio = lambda url: self.c.session.get(
            url, headers=self.c.header, allow_redirects=False
        ).content
        a1 = (rio(s.cdn(0)), rio(s.cdn(1)), rio(s.cdn(2)), floor(int(s.conf['spt'])))
        (j := Jigsaw(*a1)).save(*a1)
        self.assertGreater(j.width, 0)

    def testVerify(self):
        r = self.c.verify()
        self.assertTrue(r['randstr'])


class TestVM(TestCase):
    def setUp(self) -> None:
        import yaml
        with open('config/user.yml') as f:
            q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))
            r = q.check()
            assert r[0] == 1
            c = q.captcha(r[6])
            c.prehandle(q.xlogin_url)
            c.getTdx(c.iframe())
            self.v = c.vm

    def testGetInfo(self):
        self.assertTrue(d := self.v.getInfo())
        self.assertTrue(d['info'])
        print(d)

    def testCollectData(self):
        self.v.setData({'clientType': 2})
        self.v.setData({'coordinate': [10, 24, 0.4103]})
        self.v.setData({
            'trycnt': 1,
            'refreshcnt': 0,
            'slideValue': Captcha.imitateDrag(230),
            'dragobj': 1
        })
        self.v.setData({'ft': 'qf_7P_n_H'})
        self.assertTrue(d := self.v.getData())
        print()
        print(d)
        print(len(d))

    def testGetCookie(self):
        self.assertTrue(d := self.v.getCookie())
        print(d)
