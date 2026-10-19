import hashlib
import json
from pathlib import Path
import subprocess
import sys
BASE = Path(__file__).resolve().parent
BASELINE_FREEZE = 'fc1df491b9bdeafc1781b166752b61b7e6aa090a3aee563673edb8a41812ac13'
BASELINE_RESULT = 'b4f4eadb91c3c9c73c13b48bd591c2341bb48faac8d96a24352b34bf7c23901c'

def run(out, lean):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, '-I', '-S', str(BASE / 'baseline/verify.py'),
        '--source-only', '--freeze-sha', BASELINE_FREEZE, '--lean', str(lean), '--replay', str(out / 'baseline')]
    result = subprocess.run(command, text=True, capture_output=True)
    (out / 'baseline-command.json').write_text(json.dumps(dict(command=command, exit=result.returncode,
        stdout=result.stdout, stderr=result.stderr), indent=2) + '\n')
    assert result.returncode == 0, (result.stdout, result.stderr)
    baseline = json.loads((out / 'baseline/RECEIPT.json').read_text())
    assert baseline['result_sha256'] == BASELINE_RESULT
    import effect_audit
    import effect_run
    audit = effect_audit.run()
    effects = effect_run.run(out / 'effects', out / 'baseline', lean)
    summary = dict(baselineResult=baseline['result_sha256'], effects=effects, effectSourceBinding=audit)
    digest = hashlib.sha256(json.dumps(summary, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    (out / 'RESULT.json').write_text(json.dumps(summary, indent=2) + '\n')
    receipt = dict(status='PASS', semanticResult=digest, baselineTheorems=66,
        supplementTheorems=effects['theorems'], nativeVariants=17, leanVariants=17)
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt
