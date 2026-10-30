import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urljoin

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WPT = ROOT / "testing/web-platform/tests"
SELECTION = ROOT / "artifacts/css-minmax-relative-infinity-regression-selection-v3"
sys.path[:0] = [str(p) for p in (WPT / "tools/third_party").iterdir() if p.is_dir()] + [str(WPT / "tools"), str(WPT)]
import html5lib
from manifest.manifest import Manifest


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (PACKAGE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


PREVIOUS = ROOT / "artifacts/css-minmax-relative-infinity-broader-plan-v2"
assert digest(PREVIOUS / "FILES.json") == "10d7f9a51a01b29c4eabff58c3e767cbf3d164d8050db5c8f28c848ec7b5165a"
for name, record in json.loads((PREVIOUS / "FILES.json").read_text()).items():
    assert digest(PREVIOUS / name) == record["sha256"]
previous = json.loads((PREVIOUS / "CAPTURE.json").read_text())
providers = {record["source"]: PREVIOUS / record["capture"] for record in previous["files"]}
previous_absences = set(previous["absent_paths"])


def provider(source):
    if source in providers:
        return providers[source]
    assert source.startswith("artifacts/"), source
    return ROOT / source


records = []
absences = []


def capture(source, destination, expected=None):
    original_source = source
    source = provider(source)
    if expected is not None:
        assert digest(source) == expected, source
    target = PACKAGE / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert digest(source) == digest(target)
    records.append({"source": original_source, "read_from": str(source.relative_to(ROOT)), "capture": destination,
                    "sha256": digest(target), "bytes": target.stat().st_size})


assert digest(SELECTION / "FILES.json") == "918d866f4e68da0adfe82ff262acd563fcdf402a95fd2401a567fa96027c5263"
selection_manifest = json.loads((SELECTION / "FILES.json").read_text())
for name, record in selection_manifest.items():
    assert digest(SELECTION / name) == record["sha256"], name
selection = json.loads((SELECTION / "SELECTION.json").read_text())
references = json.loads((SELECTION / "REFERENCES.json").read_text())
pages = []
for item in selection["existing_pages"]:
    path = str(Path(item["path"]).relative_to("testing/web-platform/tests"))
    capture(item["path"], "capture/tests/" + path, item["sha256"])
    pages.append(path)
for key in ["unchanged_target_fixture", "extension_fixture"]:
    source = selection[key]
    expected = references.get(source)
    if expected is None:
        expected = selection_manifest[Path(source).name]["sha256"]
    path = "css/css-values/" + Path(source).name
    capture(source, "capture/tests/" + path, expected)
    pages.append(path)
assert len(pages) == 12

resources = set()
scripts_by_page = {}
for path in pages:
    document = html5lib.parse((PACKAGE / "capture/tests" / path).read_text(), namespaceHTMLElements=False)
    scripts = []
    for node in document.iter("script"):
        if node.get("src"):
            resource = urljoin("/" + path, node.get("src")).lstrip("/")
            assert ":" not in resource and ".." not in Path(resource).parts
            resources.add(resource)
            scripts.append({"resource": resource})
        else:
            scripts.append({"inline": node.text or ""})
    scripts_by_page[path] = scripts
assert resources == {"resources/testharness.js", "resources/testharnessreport.js",
                     "css/support/numeric-testcommon.js", "css/support/serialize-testcommon.js",
                     "css/support/computed-testcommon.js", "css/support/parsing-testcommon.js"}
for path in sorted(resources):
    capture("testing/web-platform/tests/" + path, "capture/tests/" + path)

headers = set()
for path in pages + sorted(resources):
    headers.add(path + ".headers")
    for parent in Path(path).parents:
        headers.add(str(parent / "__dir__.headers"))
for path in sorted(headers):
    source = "testing/web-platform/tests/" + path
    if source in providers:
        capture(source, "capture/tests/" + path)
    else:
        assert source in previous_absences
        absences.append(source)

metadata = dict(selection["per_page_metadata"])
for path in selection["inherited_metadata_also_required"]:
    metadata[path] = {"sha256": digest(provider(path))}
for path in pages[-2:]:
    metadata["testing/web-platform/meta/" + path + ".ini"] = {"sha256": None}
for source, expected in sorted(metadata.items()):
    if expected["sha256"] is None:
        assert source in previous_absences, source
        absences.append(source)
    else:
        path = str(Path(source).relative_to("testing/web-platform/meta"))
        capture(source, "capture/meta/" + path, expected["sha256"])

enumerator = """const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const scripts=JSON.parse(input),names=[],context=vm.createContext({test:(fn,name)=>{if(typeof fn!=='function'||typeof name!=='string')throw Error('invalid registration');names.push(name);}});try{for(const s of scripts)vm.runInContext(s.code,context,{filename:s.path,timeout:1000});process.stdout.write(JSON.stringify({complete:true,names}));}catch(e){process.stdout.write(JSON.stringify({complete:false,names:null,error:String(e),registered_before_error:names.length}));}});"""
roster = {}
for path, scripts in scripts_by_page.items():
    inputs = []
    for index, script in enumerate(scripts):
        resource = script.get("resource")
        if resource in {"resources/testharness.js", "resources/testharnessreport.js"}:
            continue
        inputs.append({"path": resource or path + ":inline:" + str(index),
                       "code": (PACKAGE / "capture/tests" / resource).read_text() if resource else script["inline"]})
    result = subprocess.run(["node", "-e", enumerator], input=json.dumps(inputs),
                            text=True, capture_output=True, check=True)
    record = json.loads(result.stdout)
    if record["complete"]:
        assert len(record["names"]) == len(set(record["names"])), path
        record["count"] = len(record["names"])
    else:
        assert "document is not defined" in record["error"], record
    roster["/" + path] = record
assert sum(record["complete"] for record in roster.values()) == 5
assert roster["/css/css-values/minmax-relative-infinity.html"]["count"] == 18
assert roster["/css/css-values/minmax-relative-infinity-ordering.html"]["count"] == 14

with tempfile.TemporaryDirectory(prefix="css-minmax-broader-manifest-") as temporary:
    scratch = Path(temporary)
    for path in pages:
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE / "capture/tests" / path, target)
    manifest = Manifest(str(scratch), "/")
    manifest.update([(path, None, True) for path in pages], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    entries = serialized["items"]["testharness"]["css"]["css-values"]
    assert set(entries) == {Path(path).name for path in pages}
    assert all(len(entry) == 2 and entry[1][0] is None for entry in entries.values())
    write_json("SUBSET-MANIFEST.json", serialized)

for record in records:
    assert digest(ROOT / record["read_from"]) == record["sha256"]
write_json("CAPTURE.json", {"pages": ["/" + path for path in pages], "files": records,
                            "absent_paths": sorted(set(absences))})
write_json("ROSTER.json", {"aggregate_callback_count": None, "callbacks_executed": False,
                           "dom_mocks": False, "pages": roster})
write_json("REFERENCES.json", {str((PREVIOUS / "FILES.json").relative_to(ROOT)): digest(PREVIOUS / "FILES.json"), str((SELECTION / "FILES.json").relative_to(ROOT)): digest(SELECTION / "FILES.json"),
                               "artifacts/css-minmax-relative-infinity-audit-v1/FILES.json": references["artifacts/css-minmax-relative-infinity-audit-v1/FILES.json"]})
print(json.dumps({"pages": len(pages), "captured_files": len(records),
                  "capture_bytes": sum(record["bytes"] for record in records),
                  "complete_inert_rosters": {path: row["count"] for path, row in roster.items() if row["complete"]},
                  "dom_required_pages": [path for path, row in roster.items() if not row["complete"]],
                  "aggregate_callback_count": None, "callbacks_executed": False,
                  "scratch_removed": True, "genuine_manifest_pages": len(entries)}))
