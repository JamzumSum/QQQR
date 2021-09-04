from os import environ as env
from unittest import TestCase
from tencentlogin import TencentLoginError

from tencentlogin.constants import QzoneAppid, QzoneProxy, StatusCode
from tencentlogin.up import UPLogin, User

login = UPLogin(
    QzoneAppid, QzoneProxy, User(
        env.get('TEST_UIN'),
        env.get('TEST_PASSWORD'),
    )
)


class TestRequest(TestCase):
    def testEncodePwd(self):
        r = login.request().check()
        if r.code == 1:
            r = login.passVC(r)
        if r.code != 1:
            self.assertTrue(r.verifycode)
            self.assertTrue(r.salt)
            p = login.encodePwd(r)
            self.assertTrue(p)

    def testLogin(self):
        r = login.check()
        try:
            self.assertTrue(login.login(r))
        except TencentLoginError as e:
            if e.code == StatusCode.RiskyNetwork:
                self.skipTest(str(e))
            else:
                raise e
