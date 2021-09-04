from tencentlogin.qr import QRLogin
from tencentlogin.constants import QzoneAppid, QzoneProxy
from unittest import TestCase


def __init__():
    global login
    login = QRLogin(QzoneAppid, QzoneProxy)


class TestQR(TestCase):
    def test0000(self):
        __init__()

    def test0_Norm(self):
        login.request()

    def test1_Refresh(self):
        b = login.show()
        self.assertTrue(b)

    def test3_Loop(self):
        with open('tmp/r.png', 'wb') as f:
            sched = login.loop()(
                refresh_callback=lambda i: print('png write: tmp/r.png') or f.write(i),
                return_callback=lambda i: self.assertIsInstance(i, str),
            )
            try:
                sched.start()
            except TimeoutError:
                # do something
                self.skipTest('User did not interact')
