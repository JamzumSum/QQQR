# TenSent Login Simulation

A simulation of T&thinsp;en&thinsp;c&thinsp;en&thinsp;t Login Protocol

## QR Login

### Get a QRcode

~~~ python
from tencentlogin.qr import QRLogin
from tencentlogin.constants import APPID, QzoneProxy

sim = QRLogin(APPID.Qzone, QzoneProxy)
png = sim.request().show()
with open('tmp/qr.png', 'wb') as f:
    f.write(png)
~~~

### Poll Status of the latest QR

~~~ python
from tencentlogin.constants import StatusCode

for _ in range(10):
    r = sim.pollStat()
    if r[0] == StatusCode.Expired: 
        # expired
        with open('tmp/qr.png', 'wb') as f: 
            f.write(sim.show())
    elif r[0] == StatusCode.Authenticated: 
        # login success
        break   
    else: 
        if r[0] != StatusCode.Waiting: 
            print(r[4])  # show msg
    sleep(3000)
else:
    # Timeout logic
    raise TimeoutError
~~~

### Login

~~~ python
r = sim.pollStat()
if r[0] == 0:
    p_skey = sim.login()
~~~

### Loop: Simpler API

~~~ python
try:
    for i in self.q.loop():
        if isinstance(i, bytes):
            with open('tmp/r.png', 'wb') as f:
                f.write(i)
except TimeoutError:
    # Timeout logic
else:
    p_skey = i
~~~

## UP Login

> NOTE: no captcha, no login protect, etc.

### Login Directly

~~~ python
import yaml
from tencentlogin.up import UPLogin, User
from tencentlogin.constants import QzoneAppid, QzoneProxy

with open('me.yml') as f:
    q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))

r = self.q.check()
if r[0] == 0:
    p_skey = self.q.login(r)
else:
    raise RuntimeError(f"Code {r[0]}: {r[4]}")
~~~

## Dependencies

- QR login requires `requests`, which is mostly a standard library.
- Additionally, UP login requires `PyExecJS`, which needs JS runtime.
  - `Node.js` is used as our test environment.

## License

- [AGPL-3.0](https://github.com/JamzumSum/QQQR/blob/master/LICENCE)
- All commercial uses are __NOT__ supported
