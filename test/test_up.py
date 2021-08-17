from tencentlogin.up import UPLogin, User
from tencentlogin.constants import QzoneAppid, QzoneProxy
from unittest import TestCase


class TestRequest(TestCase):
    def setUp(self) -> None:
        import yaml
        with open('config/user.yml') as f:
            self.q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))

    def testEncodePwd(self):
        r = self.q.check()
        if r[0] == 0:
            p = self.q.encodePwd(r)
            self.assertTrue(p)
            print(p)
        else:
            print(r)

    def testLogin(self):
        r = self.q.request().check()
        k = self.q.login(r)
        self.assertTrue(k)
        print(k)
