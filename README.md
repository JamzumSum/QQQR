# TencentQR

A simulation of QR protocol for QR login

## Usage

### Get a QRcode

~~~ python
from tencentqr import TencentQR
from tencentqr.constants import APPID, QzoneProxy

sim = TencentQR(APPID['qzone'], QzoneProxy)
png = sim.request().show()
with open('tmp/qr.png', 'wb') as f:
    f.write(png)
~~~

### Poll Status of the latest QR

~~~ python
for _ in range(10):
    r = sim.pollStat()
    if r[0] == 65: # expire
        with open('tmp/qr.png', 'wb') as f: f.write(sim.show())
    elif r[0] == 0: break   # login success
    else: 
        if r[0] != 66: print(r[4])  # other code
        sleep(3000)
~~~

### Login

~~~ python
r = sim.pollStat()
if r[0] == 0:
    p_skey = sim.login()
~~~

## License

- [AGPL-3.0](https://github.com/JamzumSum/QQQR/blob/master/LICENCE)
- All commercial uses are __NOT__ supported
