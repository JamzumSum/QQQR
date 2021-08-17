var window = new Proxy({}, {
    get: (targ, name) => {
        if (targ[name] !== undefined) return targ[name];
        else if (name == 'window') return window;
        else return global[name];
    }
});
window.sessionStorage = window.localStorage = {
    getItem: function (k) {
        return this.d[k]
    },
    setItem: function (k, v) {
        this.d[k] = v
    },
    d: {},
};
window.navigator = {
    userAgent: ua,
    getBattery: new Promise(function (resolve, reject) {
        resolve({
            charging: false,
            chargingTime: Infinity,
            dischargingTime: 20421,
            level: 0.62,
            onchargingchange: null,
            onchargingtimechange: null,
            ondischargingtimechange: null,
            onlevelchange: null,
        })
    }),
};
window.location = { href: href }; window.screen = { 'colorDepth': 24 };
window.document = {
    charset: "UTF-8",
    location: window.location,
    cookie: cookie,
    referrer: 'https://xui.ptlogin2.qq.com/',
    documentElement: {
        clientWidth: 300,
        clientHeight: 230,
    },
    body: {},
    createElement: (e) => {
        return {
            attr: {},
            child: [],
            setAttribute: function (k, v) { self.attr[k] = v; if (k == 'id') window.document[v] = this },
            removeAttribute: function (k) { self.attr[k] = undefined },
            appendChild: function (e) { this.child.push(e) }
        }
    },
    getElementById: (id) => {
        return window.document.createElement(window.document.body[id])
    }
};
