from tencentlogin.qr import QRLogin
from tencentlogin.constants import QzoneAppid, QzoneProxy
from unittest import TestCase


class TestQR(TestCase):
    def setUp(self) -> None:
        self.q = QRLogin(QzoneAppid, QzoneProxy)

    def testNorm(self):
        self.q.request()

    def testRefresh(self):
        b = self.q.request().show()
        with open('tmp/r.png', 'wb') as f:
            f.write(b)
        for _ in range(10):
            r = self.q.pollStat()
            self.assertTrue(r)

    def testLogin(self):
        b = self.q.request().show()
        with open('tmp/r.png', 'wb') as f:
            f.write(b)
        for _ in range(10):
            r = self.q.pollStat()
            if r[2]:
                k = self.q.login()
                break

        self.assertTrue(k)

    def testLoop(self):
        with open('tmp/r.png', 'wb') as f:
            sched = self.q.loop()(
                refresh_callback=lambda i: f.write(i),
                return_callback=lambda i: self.assertIsInstance(i, str) or print(i),
            )
            try:
                sched.start()
            except TimeoutError:
                # do something
                pass
