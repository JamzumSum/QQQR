from os import environ as env

import pytest
from qqqr.constants import QzoneAppid, QzoneProxy, StatusCode
from qqqr.qr import QRLogin

need_interact = pytest.mark.skipif(
    not env.get('QR_OK', 0), reason='need user interaction'
)


@pytest.fixture(scope='module')
def login():
    login = QRLogin(QzoneAppid, QzoneProxy)
    login.request()
    yield login


class TestProcedure:
    def test_new(self, login):
        assert login.show()
        assert isinstance(login.qrsig, str)

    def test_poll(self, login):
        assert (r := login.pollStat())
        assert r[0] == StatusCode.Waiting


class TestLoop:
    @staticmethod
    def writeqr(b: bytes):
        with open('tmp/r.png', 'wb') as f:
            f.write(b)

    @need_interact
    def test_Loop(self, login):
        thread = login.loop(self.writeqr)
        cookie = thread.result()
        assert cookie['p_skey']

    def test_stop(self, login):
        thread = login.loop(lambda _: 0)
        thread.stop()
