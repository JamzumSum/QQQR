import subprocess
from functools import partial


class ExecJS:
    def __init__(self, node: str = 'node', *, js=None, path=None):
        assert bool(js) ^ bool(path)

        self.node = node
        if path:
            with open(path, encoding='utf8') as f:
                js = f.read()
        self.js = js

        self.que = []

    @staticmethod
    def callstr(func, *args) -> str:
        quoted = (
            tostr[ty]() if (ty := type(i)) in (tostr := {
                str: lambda: f'"{i}"',
                bool: lambda: {True: 'true', False: 'false'}[i]
            }) else str(i) for i in args
        )
        return f'{func}({",".join(quoted)})'

    def addfunc(self, func: str, *args):
        self.que.append((func, *args))

    def _exec(self, js):
        p = subprocess.Popen(
            *self.node.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate(js.encode())
        if stderr:
            raise RuntimeError(stderr.decode())
        return stdout.decode()

    def __call__(self, func: str, *args) -> str:
        js = self.js
        for i in self.que:
            js += self.callstr(*i)
            js += ';'
        self.que.clear()
        js += f'\nconsole.log({self.callstr(func, *args)});'
        return self._exec(js)

    def get(self, prop: str):
        js = self.js + f'\nconsole.log({prop});'
        return self._exec(js)

    def bind(self, func: str, new=True):
        n = ExecJS(self.node, js=self.js) if new else self
        return partial(n.__call__, func)
