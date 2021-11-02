import asyncio
from os import environ as env

import pytest
from qqqr.constants import QzoneAppid, QzoneProxy, StatusCode
from qqqr.exception import TencentLoginError
from qqqr.up import UPLogin, User


@pytest.fixture(scope='module')
def login():
    login = UPLogin(
        QzoneAppid, QzoneProxy, User(env.get('TEST_UIN'), env.get('TEST_PASSWORD'))
    )
    login.request()
    yield login


class TestRequest:
    def testEncodePwd(self, login):
        r = login.check()
        if r.code == 1:
            r = login.passVC(r)
        if r.code != 1:
            assert r.verifycode
            assert r.salt
            assert login.encodePwd(r)

    def testLogin(self, login):
        r = login.check()
        try:
            assert login.login(r)
        except TencentLoginError as e:
            if e.code in [StatusCode.RiskyNetwork, StatusCode.ForceQR]:
                pytest.skip(str(e))
            else:
                raise e
