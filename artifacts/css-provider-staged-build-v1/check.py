import ast
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
src = (HERE / 'build.py').read_text()
ast.parse(src)
assert src.rindex('ownership.quiescent(HERE)') < src.index("s.save(directory / 'COMMAND.json'") < src.index('builder.run(')
tree = ast.parse((ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py').read_text())
function = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'quiescent')
def need(condition,message):
    if not condition: raise AssertionError(message)
namespace={'need':need}
exec(compile(ast.Module(body=[function],type_ignores=[]),'quiescence','exec'),namespace)
with tempfile.TemporaryDirectory(prefix='provider-build-guard-',dir='/private/tmp') as temp:
    runtime=Path(temp); own=runtime/'own-build';own.mkdir()
    namespace['quiescent'](runtime)
    (own/'COMMAND.json').write_text('{}')
    try:namespace['quiescent'](runtime)
    except AssertionError:pass
    else:raise AssertionError('unfinished command accepted')
    (own/'RESULT.json').write_text('{}')
    namespace['quiescent'](runtime)
assert not Path(temp).exists()
(HERE/'CHECK.json').write_text(json.dumps({'syntax':True,'own_command_after_final_quiescence':True,'unfinished_command_rejected':True,'terminal_command_accepted':True,'scratch_removed':True,'build_executed':False,'live_state_queries':False},indent=2)+'\n')
print('Quiescence ordering and scratch control passed; no live/runtime changes')
