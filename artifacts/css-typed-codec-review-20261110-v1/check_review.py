from pathlib import Path
import hashlib, json, subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
r = json.loads((P / "REVIEWED.json").read_text())
owner = ROOT / r["owner_capsule"]
h = lambda b: hashlib.sha256(b).hexdigest()
assert h((owner / "SOURCE-ONLY.json").read_bytes()) == r["source_manifest_sha256"]
assert json.loads((owner / "SOURCE-ONLY.json").read_text()) == r["files"]
for name, digest in r["files"].items(): assert h((owner / name).read_bytes()) == digest, name
positive = json.loads((P / r["independent_positive_replay"]).read_text())
assert positive["status"] == "PASS"
for name, digest in positive["files"].items(): assert r["files"][name] == digest, name
author_path = owner / r["author_verification_report"]
assert h(author_path.read_bytes()) == r["author_verification_sha256"]
author = json.loads(author_path.read_text())
assert positive["audits"] == author["audits"]
for name in ["same-type-index", "same-type-opcode", "scan-budget", "guard-bypassed", "scope-check-lost", "json-opcode", "extra-field-admitted"]:
    for suffix, expected in [("witness-positive", 0), ("typecheck", 0), ("laws", 1), ("witness", 1)]:
        key = name + "-" + suffix
        assert h((author_path.parent / (key + ".log")).read_bytes()) == author["commands"][key]["output_sha256"]
        assert author["commands"][key]["exit"] == expected
origin = json.loads((owner / "ROOT-ORIGINS.json").read_text())
for item in origin["files"]:
    data = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show", origin["origin_commit"] + ":" + item["origin"]], cwd=ROOT)
    assert h(data) == item["sha256"] and data == (owner / item["destination"]).read_bytes()
assert not list(P.rglob("*.olean"))
result = {"status":"PASS", "frozen_inputs":len(r["files"]), "independent_audits":len(positive["audits"]), "new_declarations":len(author["new_declarations"]), "kernel_boundary_cases":len(author["kernel_cases"]), "independent_execution_rows_each":positive["runtime_rows_each"], "independent_parser_observations":positive["parser_rows"], "independent_invalid_documents":positive["independent_invalid_documents"], "author_semantic_receipts_verified":7, "git_origins":len(origin["files"]), "source_manifest_sha256":r["source_manifest_sha256"]}
(P / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
