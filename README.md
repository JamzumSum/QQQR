# TenSent Login Simulation

A simulation of T&thinsp;en&thinsp;c&thinsp;en&thinsp;t Login Protocol

## QR Login

### Get a QRcode

~~~ python
from tencentlogin.qr import QRLogin
from tencentlogin.constants import QzoneAppid, QzoneProxy

sim = QRLogin(QzoneAppid, QzoneProxy)
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
from tencentlogin.qr import QRLogin
from tencentlogin.constants import QzoneAppid, QzoneProxy

sim = QRLogin(QzoneAppid, QzoneProxy)
sched = sim.loop()(
    refresh_callback=lambda png: show_user_qr(png),
    return_callback=lambda cookie: return_cookie(cookie),
)
try:
    sched.start()
except TimeoutError:
    # do something when refresh times exceeded
    pass
except KeyboardInterrupt:
    # do something when interupted
    pass
~~~

~~~ python
# other thread (maybe manually called by user)
sched.stop(exception=True)    # raise KeyboardInterrupt
~~~

## UP Login

> NOTE: tcaptcha support is an experimental feature!

### Login Directly

~~~ python
import yaml
from tencentlogin.up import UPLogin, User
from tencentlogin.constants import QzoneAppid, QzoneProxy

with open('me.yml') as f:
    q = UPLogin(QzoneAppid, QzoneProxy, User(**yaml.safe_load(f)))

r = self.q.check()
p_skey = self.q.login(r)
~~~

## Dependencies

- requests
- For async waiting for QR scanning, `apscheduler` is needed. 
- For User-Password login, `nodejs` is needed. `node` will be called by default.
- For passing tcaptcha, `opencv-python` is needed.

## License

- [AGPL-3.0](https://github.com/JamzumSum/QQQR/blob/master/LICENCE)
- All commercial uses are __NOT__ supported
