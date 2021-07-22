from tencentqr import TencentQR
from tencentqr.constants import QzoneAppid, QzoneProxy
from unittest import TestCase


class TestRequest(TestCase):
    def setUp(self) -> None:
        self.q = TencentQR(QzoneAppid, QzoneProxy)

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
        try:
            for i in self.q.loop():
                if isinstance(i, bytes):
                    with open('tmp/r.png', 'wb') as f:
                        f.write(i)
        except TimeoutError:
            pass
        else:
            print(i)
            self.assertIsInstance(i, str)
