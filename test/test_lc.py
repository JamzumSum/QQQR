import sys
from os import environ as env

import pytest
from tencentlogin.constants import QzoneAppid, QzoneProxy, StatusCode
from tencentlogin.lc import LCLogin

needuser = pytest.mark.skipif(sys.platform != 'win32', reason='need user interaction')


def setup_module():
    global login
    login = LCLogin(QzoneAppid, QzoneProxy, env.get('TEST_UIN'))
    # login.request()


@needuser
def test_local():
    login.checkLoginList()
    login.login()
