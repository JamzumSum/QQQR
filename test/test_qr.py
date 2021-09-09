import sys

import pytest
from tencentlogin.constants import QzoneAppid, QzoneProxy, StatusCode
from tencentlogin.qr import QRLogin

needuser = pytest.mark.skipif(sys.platform != 'win32', reason='need user interaction')


def setup_module():
    global login
    login = QRLogin(QzoneAppid, QzoneProxy)
    login.request()


class TestProcedure:
    def test_new(self):
        assert login.show()

    def test_poll(self):
        assert (r := login.pollStat())
        assert r[0] == StatusCode.Waiting


@needuser
class TestLoop:
    def assertIsInstance(self, o, cls):
        assert isinstance(o, cls)

    def test_Loop(self):
        with open('tmp/r.png', 'wb') as f:
            sched = login.loop()(
                refresh_callback=lambda i: print('png write: tmp/r.png') or f.write(i),
                return_callback=lambda i: self.assertIsInstance(i, str),
            )
            try:
                sched.start()
            except TimeoutError:
                # do something
                pytest.skip('User did not interact')
