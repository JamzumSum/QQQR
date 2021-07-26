'''
date: 2021-07-20
'''

from . import Proxy, APPID
from enum import IntEnum

QzoneProxy = Proxy(
    'https://qzs.qq.com/qzone/v6/portal/proxy.html',
    'https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone'
)

QzoneAppid = APPID(549000912, 5)


class StatusCode(IntEnum):
    # Unified
    Authenticated = 0
    # QR
    Expired = 65
    Waiting = 66
    Scanned = 67
    # UP
    WrongPwdOrUin = 3
