from tencentqr import TencentQR
from tencentqr.constants import APPID, QzoneProxy
from unittest import TestCase


class TestRequest(TestCase):
    def setUp(self) -> None:
        self.q = TencentQR(APPID['qzone'], QzoneProxy)

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
                k = self.q.login(r[2])
                break

        self.assertTrue(k)
