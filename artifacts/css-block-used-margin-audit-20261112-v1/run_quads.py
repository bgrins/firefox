import importlib.util
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
out = HERE / 'quads'
assert not out.exists()
out.mkdir()
source = (HERE / 'diagnostic.html').read_text()
needle = '        width: rect.width,\n'
assert source.count(needle) == 1
source = source.replace(needle, needle + '''        quad: typeof child.getBoxQuads === "function"
          ? child.getBoxQuads({box: "margin", relativeTo: parent}).map(q => ({
              x: q.bounds.x, width: q.bounds.width,
              startX: q.p1.x, endX: q.p2.x,
            })) : null,
''')
(out / 'diagnostic.html').write_text(source)
shutil.copyfile(HERE / 'process.py', out / 'process.py')
spec = importlib.util.spec_from_file_location('probe_runner', HERE / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.HERE = out
module.main()
