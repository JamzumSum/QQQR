# TencentQR

A simulation of QR protocol for QR login

## Usage

### Get a QRcode

~~~ python
from tencentqr import TencentQR
from tencentqr.constants import APPID, QzoneProxy

sim = TencentQR(APPID.Qzone, QzoneProxy)
png = sim.request().show()
with open('tmp/qr.png', 'wb') as f:
    f.write(png)
~~~

### Poll Status of the latest QR

~~~ python
from tencentqr.constants import StatusCode

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

### Loop: Simpler api

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

## License

- [AGPL-3.0](https://github.com/JamzumSum/QQQR/blob/master/LICENCE)
- All commercial uses are __NOT__ supported
