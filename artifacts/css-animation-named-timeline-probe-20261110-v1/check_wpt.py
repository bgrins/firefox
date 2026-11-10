import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / "testing/web-platform/tests"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Use python3 -I without -O")
    sys.dont_write_bytecode = True
    sys.path[:0] = [
        str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()
    ] + [str(WPT / "tools"), str(WPT), str(ROOT / "third_party/python/pyyaml/lib")]
    import html5lib
    from manifest.manifest import Manifest

    from tools.lint import lint

    output = HERE / sys.argv[1]
    output.mkdir()
    relative = "css/css-animations/named-timeline-admission.html"
    resources = {
        "/" + relative: HERE / "named-timeline-admission.html",
        "/resources/testharness.js": WPT / "resources/testharness.js",
        "/resources/testharnessreport.js": WPT / "resources/testharnessreport.js",
    }
    dom = html5lib.parse(
        resources["/" + relative].read_text(), namespaceHTMLElements=False
    )
    scripts = [node.text or "" for node in dom.iter("script") if not node.get("src")]
    assert len(scripts) == 1
    source = scripts[0]
    program = """
const vm = require('vm');
let source = '';
process.stdin.on('data', chunk => source += chunk);
process.stdin.on('end', () => {
  const names = [];
  vm.runInNewContext(source, {window: {}, promise_test: (_, name) => names.push(name)});
  process.stdout.write(JSON.stringify(names));
});
"""
    with tempfile.TemporaryDirectory(
        prefix="named-timeline-admission-"
    ) as directory:
        staging = Path(directory)
        for url, path in resources.items():
            target = staging / url.lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        js = staging / "check.js"
        js.write_text(source)
        subprocess.run(
            ["node", "--check", str(js)], check=True, capture_output=True, text=True
        )
        result = subprocess.run(
            ["node", "-e", program],
            input=source,
            text=True,
            capture_output=True,
            check=True,
        )
        names = json.loads(result.stdout)
        assert names == [
            "Named timeline admission: " + mode
            for mode in ["smil-scroll", "normal-scroll", "smil-scope-only"]
        ]
        primary = source[
            source.index('    mark(mode, "stimulus-begin");') : source.index(
                "    observation.after"
            )
        ]
        assert "await " not in primary and "getAnimations" not in primary
        assert primary.count("getComputedStyle") == 1
        assert primary.index("svg.setCurrentTime(75)") < primary.index(
            "getComputedStyle(outside)"
        )
        assert source.index("getComputedStyle(host).display") < source.index(
            'mark(mode, "stimulus-begin")'
        )
        before = source[:source.index('    mark(mode, "stimulus-begin");')]
        assert "getComputedStyle(provider)" not in source
        assert 'getElementById("provider")' not in before
        assert 'observation.after = animationState(animation)' in source
        assert primary.index('mark(mode, "getter-return"') > primary.index(
            "getComputedStyle(outside)"
        )
        for token in ["scrollTop", "getComputedTiming", "animationState", "requestAnimationFrame"]:
            assert token not in primary
        for field in ["font", "timelineSource", "timing.progress", "playState", "pending"]:
            assert "observation.before." + field in before
        assert 'scopeOnly ? "fallback" : "provider"' in source
        assert source.count('id="provider"') == 1
        assert source.count('id="outside"') == 1
        assert source.count('id="fallback"') == 1
        findings = lint.check_path(str(staging), relative) + lint.check_file_contents(
            str(staging), relative
        )
        assert not findings, findings
        manifest = Manifest(str(staging), "/")
        manifest.update(
            [(url.lstrip("/"), None, True) for url in resources], parallel=False
        )
        entries = [
            {"path": path, "url": item.url}
            for kind, path, items in manifest
            if kind == "testharness"
            for item in items
        ]
        assert entries == [{"path": relative, "url": "/" + relative}]
        outputs = {
            "MANIFEST.json": manifest.to_json(),
            "ROSTER.json": {"/" + relative: names},
            "LINT.json": {relative: findings},
            "INPUTS.json": {
                "resources": {
                    url: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                    for url, path in resources.items()
                },
                "prefs": {
                    "dom.window.dump.enabled": True,
                    "layout.css.display-animations.enabled": False,
                    "layout.css.scroll-driven-animations.enabled": True,
                },
            },
        }
        for name, data in outputs.items():
            (output / name).write_text(json.dumps(data, indent=2) + "\n")
    assert not staging.exists()
    (output / "RESULT.json").write_text(
        json.dumps(
            {
                "pages": entries,
                "callbacks": len(names),
                "browser_execution": False,
                "genuine_wpt_lint_and_manifest": True,
                "node_syntax_and_inert_registration": True,
                "primary_getter_order_checked": True,
                "hidden_provider_not_queried_before_stimulus": True,
                "baseline_admission_assertions_present": True,
                "scratch_removed": True,
                "source_hashes": {
                    name: sha(HERE / name)
                    for name in ["check_wpt.py", "named-timeline-admission.html"]
                },
            },
            indent=2,
        )
        + "\n"
    )
    print("3 callbacks prepared; syntax, registration, WPT lint and manifest passed")


if __name__ == "__main__":
    main()
