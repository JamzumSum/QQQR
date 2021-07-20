'''
date: 2021-07-20
'''

from . import Proxy

QzoneProxy = Proxy(
    'https://qzs.qq.com/qzone/v6/portal/proxy.html',
    'https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone'
)

APPID = {
    'qzone': 549000912,
}
