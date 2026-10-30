import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [
    str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

page = "animation-duration-updatetiming-after-contextual-feedback.tentative.html"
old = ROOT / "artifacts/css-contextual-duration-feedback-consistency-probe-v2"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = (HERE / page).read_text()
previous = (old / "animation-duration-feedback-consistency-observation.tentative.html").read_text()
assert sha(old / "animation-duration-feedback-consistency-observation.tentative.html") == "bf81bb09a6fb19e8abf19fdb9d625c3dfc8f03365eba4b41cebbdd33d50ac251"
start, end = "function styleOf", "function create"
assert source[source.index(start):source.index(end)] == previous[previous.index(start):previous.index(end)]
assert "fetch(" not in source and "console." not in source
batch = source[source.index("for (const [duration, time]"):source.index('await collect("batched-final-2000"')]
assert all(word not in batch for word in ["await", "getComputedStyle", "read(", "outline", "classList"])
assert '[[1800, 700], [2500, 900], [2000, 1000]]' in batch
assert source.index('await collect("unchanged-batch"') < source.index('for (const trajectory of trajectories) assertFixedTiming')
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter("script") if not node.get("src")]
assert len(scripts) == 1 and dom.find("body").find("script") is not None
assert [node.get("src") for node in dom.iter("script") if node.get("src")] == [
    "/resources/testharness.js", "/resources/testharnessreport.js"]
program = r'''
const vm = require("vm");
let source = "";
process.stdin.on("data", x => source += x);
process.stdin.on("end", () => {
  const names = [];
  const assert = condition => { if (!condition) throw new Error("assertion"); };
  const context = vm.createContext({promise_test: (_, name) => names.push(name),
    assert_true: assert, assert_equals: (a, b) => assert(a === b),
    assert_approx_equals: (a, b, epsilon) => assert(Number.isFinite(a) && Math.abs(a-b) <= epsilon)});
  vm.runInContext(source, context);
  const verify = vm.runInContext("assertFixedTiming", context);
  function fixture(zero, role) {
    return {role, phases: Array.from({length: 6}, (_, index) => {
      const time = index < 4 ? 750 : 1000;
      const progress = time / 2000;
      const style = {font: `${zero ? 32*progress : 16+16*progress}px`, opacity: `${zero ? 1 : progress}`};
      const effects = Array.from({length: zero ? 1 : 2}, () => ({time, state: "paused", duration: 2000, progress}));
      const sample = {effects, repeatEffects: structuredClone(effects), currentEffects: structuredClone(effects),
        style, repeatStyle: structuredClone(style), afterMembershipStyle: structuredClone(style),
        sameAnimations: effects.map(() => true), sameEffects: effects.map(() => true)};
      if (role === "override" && index === 0) {
        sample.style.font = "71px";
        sample.effects.forEach(effect => { effect.duration = 0; effect.progress = null; });
      }
      return {time, name: `${index}`, reads: [sample, structuredClone(sample)]};
    })};
  }
  let positives = 0;
  for (const zero of [false, true]) for (const role of ["override", "literal"]) {
    verify(fixture(zero, role), zero); positives++;
  }
  const negatives = [];
  function reject(name, zero, role, alter) {
    const value = fixture(zero, role); alter(value);
    try { verify(value, zero); } catch (_) { negatives.push(name); return; }
    throw new Error("accepted false control: " + name);
  }
  reject("historical coupled stale font", false, "override", v => v.phases[1].reads[0].style.font = "22.85px");
  reject("historical zero-start stale font", true, "override", v => v.phases[1].reads[0].style.font = "0px");
  reject("batch leaves old composed font", false, "override", v => v.phases[4].reads[0].style.font = "22px");
  reject("batch leaves old seek time", false, "override", v => v.phases[4].reads[0].effects[0].time = 750);
  reject("batch retains intermediate duration", false, "override", v => v.phases[4].reads[0].effects[0].duration = 2500);
  reject("unchanged batch loses output", true, "override", v => v.phases[5].reads[0].repeatStyle.font = "12px");
  reject("literal calibration wrong", false, "literal", v => v.phases[0].reads[0].style.opacity = "0.5");
  reject("animation replaced", false, "override", v => v.phases[1].reads[0].sameAnimations[0] = false);
  reject("effect replaced", true, "override", v => v.phases[1].reads[0].sameEffects[0] = false);
  reject("current animation missing", true, "override", v => v.phases[1].reads[0].currentEffects = []);
  process.stdout.write(JSON.stringify({names, positives, negatives}));
});
'''
checks = json.loads(subprocess.run(["node", "-e", program], input=scripts[0], text=True,
                                   capture_output=True, check=True).stdout)
assert checks["names"] == [
    "Script duration and batched seeks recompose coupled contextual animations",
    "Script duration and batched seeks recompose zero-start contextual font animation"]
with tempfile.TemporaryDirectory(prefix="duration-reduced-queue-manifest-") as temporary:
    scratch = Path(temporary)
    folder = scratch / "css/css-animations"
    folder.mkdir(parents=True)
    shutil.copyfile(HERE / page, folder / page)
    (scratch / "lint.ignore").write_text("")
    paths = ["css/css-animations/" + page]
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True) for path in paths], parallel=False)
    actual = json.loads(json.dumps(manifest.to_json()))
    assert set(actual["items"]["testharness"]["css"]["css-animations"]) == {page}
    (HERE / "SUBSET-MANIFEST.json").write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    cwd = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), paths, "normal", jobs=1) == 0
    finally:
        os.chdir(cwd)
assert not scratch.exists()
checks.update(lint_errors=0, scratch_removed=True, browser_executed=False,
              callback_bodies_executed=False, synthetic_assertion_checks_only=True,
              ordered_read_helpers_identical=True, no_reads_inside_batch=True)
(HERE / "CHECK.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
print(json.dumps(checks, indent=2))
