'''
date: 2021-07-20
'''

from . import Proxy
from enum import IntEnum

QzoneProxy = Proxy(
    'https://qzs.qq.com/qzone/v6/portal/proxy.html',
    'https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone'
)


class APPID(IntEnum):
    Qzone = 549000912


class StatusCode(IntEnum):
    Authenticated = 0
    Expired = 65
    Waiting = 66
    Scanned = 67
