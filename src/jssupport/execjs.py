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

    def __call__(self, func: str, *args) -> str:
        quoted = (
            tostr[ty]() if (ty := type(i)) in (tostr := {
                str: lambda: f'"{i}"',
            }) else str(i) for i in args
        )
        js = self.js + f'\nconsole.log({func}({",".join(quoted)}));'

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

    def bind(self, func: str, new=True):
        n = ExecJS(self.node, js=self.js) if new else self
        return partial(n.__call__, func)
