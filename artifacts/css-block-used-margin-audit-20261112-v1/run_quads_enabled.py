import importlib.util
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
out = HERE / 'quads-enabled'
assert not out.exists()
out.mkdir()
source = (HERE / 'diagnostic.html').read_text()
needle = '        width: rect.width,\n'
assert source.count(needle) == 1
source = source.replace(needle, needle + '''        quad: child.getBoxQuads({box: "margin", relativeTo: parent}).map(q => ({
          x: q.getBounds().x, width: q.getBounds().width,
          startX: q.p1.x, endX: q.p2.x,
        })),
''')
(out / 'diagnostic.html').write_text(source)
shutil.copyfile(HERE / 'process.py', out / 'process.py')
runner = (HERE / 'run.py').read_text()
needle = "'--no-pause-after-test', '--processes=1',"
assert runner.count(needle) == 1
runner = runner.replace(needle, needle + " '--setpref=layout.css.getBoxQuads.enabled=true',")
(out / 'run.py').write_text(runner)
spec = importlib.util.spec_from_file_location('enabled_probe_runner', out / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ROOT = HERE.parents[1]
module.TARGET = module.ROOT / 'testing/web-platform/tests/css/cssom/block-used-margin-local-probe.html'
module.main()
