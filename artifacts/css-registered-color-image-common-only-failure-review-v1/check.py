import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())

def main():
    spec = importlib.util.spec_from_file_location("failure_review", HERE / "review.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config, owner = module.authenticate()
    assert config["execution_enabled"] is False
    assert not config["mutations_allowed"] and not config["epoch_publication_allowed"]
    original = ROOT / "artifacts/css-registered-color-image-common-only-terminal-review-v1/review.py"
    before, after = original.read_text(), (HERE / "review.py").read_text()
    delta = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                    fromfile="common-review-v1/review.py", tofile="failure-review-v1/review.py"))
    assert delta == (HERE / "REVIEW-DELTA.patch").read_text()
    marker = '    assert {name: sha(CONTROL / name) for name in policy["controls"]}'
    assert before[before.index(marker):] == after[after.index(marker):]
    runtime = ROOT / config["runtime_directory"]
    result = read(runtime / "CANDIDATE-RESULT.json")
    build = read(runtime / "candidate-build/build-RESULT.json")
    terminal = read(runtime / "ROOT-TERMINAL.json")
    assert terminal == config["failure_terminal_record"]
    assert config["actual_terminal"] == {"session": 16539, "launch_chunk": "335776", "terminal_chunk": "e6dc66", "exit": 1,
                                         "result_sha256": hashlib.sha256((runtime / "CANDIDATE-RESULT.json").read_bytes()).hexdigest()}
    assert build["exit"] == 0 and build["error"] is None and build["stop_reason"] is None
    assert not result["success"] and result["candidate_phase"] is None and result["restoration_verified"]
    assert read(runtime / "FAILURE-TRACEBACK.json")["error"] == result["error"] == "AssertionError()"
    for name in ("candidate-wpt", "candidate-build/RESULT.json", "OUTCOMES.json", "PHASES-PRE.json", "PHASES-POST.json"):
        assert not (runtime / name).exists() and not (runtime / name).is_symlink()
    pre = read(runtime / "CANDIDATE-PRE.json")
    post = read(runtime / "POST.json")
    raw = read(runtime / "RAW-INDEX-OBSERVATION.json")
    adjusted = copy.deepcopy(pre["snapshot"])
    assert adjusted["index"]["raw_index"] == raw["before"]
    adjusted["index"]["raw_index"] = raw["after"]
    assert adjusted == post and raw["semantic_index_unchanged"] and not raw["canonical_updated"]
    restoration = read(runtime / "RESTORATION.json")
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    for name, role in pre["sources"].items():
        assert restoration["sources"][name] == {"sha256": role["base_sha256"], "identity": role["identity"]}
    backup = read(runtime / "BACKUP-CLEANUP.json")
    assert backup == {"owned_backup_bytes": 1008605176, "removed": False, "retained_after_failure": True,
                      "verified_original_restoration": True}
    assert backup["owned_backup_bytes"] == pre["owned_backup_bytes"] == read(runtime / "BACKUPS.json")["bytes"]
    body = (runtime / "candidate-build/build.log").read_bytes()
    warnings = module.warning_summary(body)
    return {"saved_admission_passed": True, "references_authenticated": len(read(HERE / "REFERENCES.json")),
            "exact_delta_and_restoration_tail": True, "saved_pre_post_only_raw_index_changed": True,
            "source_claims_joined": 3, "owned_backup_bytes": backup["owned_backup_bytes"],
            "build_exit": 0, "owner_exit": 1, "browser_started": False,
            "build_log_sha256": hashlib.sha256(body).hexdigest(), "compiler_warnings": warnings,
            "live_restoration_verified": False, "cleanup_performed": False, "epoch_updated": False}

if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
