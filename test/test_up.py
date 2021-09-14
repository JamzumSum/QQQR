from os import environ as env

import pytest
from tencentlogin import TencentLoginError
from tencentlogin.constants import QzoneAppid, QzoneProxy, StatusCode
from tencentlogin.up import UPLogin, User

login = None


def setup_module():
    global login
    login = UPLogin(
        QzoneAppid, QzoneProxy, User(
            env.get('TEST_UIN'),
            env.get('TEST_PASSWORD'),
        )
    )
    login.request()


class TestRequest:
    def testEncodePwd(self):
        r = login.check()
        if r.code == 1:
            r = login.passVC(r)
        if r.code != 1:
            assert r.verifycode
            assert r.salt
            assert login.encodePwd(r)

    def testLogin(self):
        r = login.check()
        try:
            assert login.login(r)
        except TencentLoginError as e:
            if e.code in [StatusCode.RiskyNetwork, StatusCode.ForceQR]:
                pytest.skip(str(e))
            else:
                raise e
