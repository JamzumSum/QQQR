# TenSent Login Simulation

A simulation of T&thinsp;en&thinsp;c&thinsp;en&thinsp;t Login Protocol. This repo is a component of [Qzone2TG][qzone2tg].

<div style="text-align:left">

<img src="https://img.shields.io/badge/python-3.8%2F3.9-blue">

<a href="https://github.com/JamzumSum/QQQR/actions/workflows/interface.yml">
<img src="https://github.com/JamzumSum/QQQR/actions/workflows/interface.yml/badge.svg">
</a>

<a href="https://github.com/JamzumSum/QQQR/actions/workflows/test.yml">
<img src="https://github.com/JamzumSum/QQQR/actions/workflows/test.yml/badge.svg">
</a>

</div>

## Examples

### QR Login

~~~ python
from qqqr.qr import QRLogin
from qqqr.constants import QzoneAppid, QzoneProxy

def test_Loop(self):
    login = QRLogin(QzoneAppid, QzoneProxy).request()
    thread = login.loop(sendqr2user)    # register callback for qr bytes
    cookie = thread.result()            # block current thread
    assert cookie['p_skey']
~~~

### UP Login

> NOTE: tcaptcha support is an experimental feature!

#### Login Directly

~~~ python
from qqqr.up import UPLogin, User
from qqqr.constants import QzoneAppid, QzoneProxy

def test_login():
    login = UPLogin(QzoneAppid, QzoneProxy, User(uin, pwd)).request()
    cookie = login.login(login.check())
    assert cookie['p_skey']
~~~

## Dependency Notice

- Uin-Password login needs to execute JavaScript. `NodeJS` is used;
- `opencv-python` is needed for captcha image processing;
- `PyYaml` will be needed for cv debugging and development.

## License

- [AGPL-3.0](https://github.com/JamzumSum/QQQR/blob/master/LICENCE)
- All commercial uses are __NOT__ supported

### Third Party

- opencv-python: https://github.com/opencv/opencv-python#licensing


[qzone2tg]: https://github.com/JamzumSum/Qzone2TG "Forward Qzone Feeds to Telegram"
