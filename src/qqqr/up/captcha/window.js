var EmptyFunc = function () { };

var window = this;
var span = {
    setAttribute: EmptyFunc,
    removeAttribute: EmptyFunc,
    removeChild: EmptyFunc
};

var canvas = {
    style: {},
    getContext: function () {
        return new function () {
            this.getParameter = function (n) {
                switch (n) {
                    case 37446:
                        return "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.100.9864)";
                    case 37445:
                        return "Google Inc. (Intel)"
                }
            },
                this.getExtension = function (n) {
                    return n == "WEBGL_debug_renderer_info" ? {
                        UNMASKED_RENDERER_WEBGL: 37446,
                        UNMASKED_VENDOR_WEBGL: 37445
                    } : {}
                },
                this.beginPath = this.arc = this.closePath = this.fill = this.rect = this.isPointInPath = this.fillRect = this.fillText = EmptyFunc;
            return this;
        }
    },
    toDataURL: function () {
        return RanStr(32);
    }
};
var innerHeight = 230,
    innerWidth = 300;
var outerWidth = 1274,
    outerHeight = 792;
var screen = {
    colorDepth: 24,
    pixelDepth: 24,
    width: 1408,
    height: 792,
    availLeft: 0,
    availTop: 0,
    availWidth: 1408,
    availHeight: 792
};
var location = { href: href, protocol: "https:" };
var document = {
    charset: "UTF-8",
    cookie: cookie,
    location: location,
    referrer: 'https://xui.ptlogin2.qq.com/',
    documentElement: {
        clientWidth: 300,
        clientHeight: 230,
    },
    body: {},
    createElement: (n) => {
        switch (n) {
            case "canvas": return canvas
            case "span": return span
            default: return {
                addEventListener: EmptyFunc,
                contentWindow: {}
            };
        }
    },
    getElementsByTagName: function () {
        return [{
            appendChild: EmptyFunc,
            removeChild: EmptyFunc
        }];
    },
    getElementById: (id) => {
        return span;
    }
};
var navigator = {
    userAgent: ua,
    appVersion: ua,
    platform: 'Win32',
    cookieEnabled: true,
    languages: ["zh-CN", "en", "en-US"],
    vendor: "Google Inc.",
    appName: "Netscape",
    plugins: [],
    getBattery: function () {
        var func = function (resolve, reject) {
            resolve({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1,
                onchargingchange: null,
                onchargingtimechange: null,
                ondischargingtimechange: null,
                onlevelchange: null
            });
        }
        return obj = new Promise(func), obj.then = func, obj;
    }
};
