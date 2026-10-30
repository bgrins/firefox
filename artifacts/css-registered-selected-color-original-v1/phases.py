import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def run(root, here, output, policy, env, verify, owned, cancelled):
    spec = importlib.util.spec_from_file_location("clean_original_wpt", here / "wpt.py")
    wpt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wpt)
    initial = verify()
    wpt.save(output / "PHASES-PRE.json", initial)
    phase = output / "original-wpt"
    result = wpt.run(root, here, phase, "original", policy, env, verify, owned, cancelled)
    assessment = read(phase / "ASSESSMENT.json")
    assert assessment["complete"] and len(assessment["rows"]) == policy["wpt"]["expected_subtest_count"] and len(assessment["ends"]) == policy["wpt"]["expected_page_count"]
    assert all(row["status"] in ("PASS", "FAIL") for row in assessment["rows"])
    wpt.save(output / "OUTCOMES.json", {
        "callbacks_passed": sum(row["status"] == "PASS" for row in assessment["rows"]),
        "callbacks_failed": sum(row["status"] == "FAIL" for row in assessment["rows"]),
        "rows": assessment["rows"], "endings": assessment["ends"],
        "provider_source_role": "clean-original", "native_acceptance": False,
    })
    assert not owned and read(phase / "PRE.json") == read(phase / "POST.json") == initial
    metadata = read(phase / "APPLICATION-METADATA.json")
    assert metadata == read(phase / "APPLICATION-METADATA-POST.json")
    assert metadata["revision"] == metadata["build_revision"] == policy["head"]
    assert metadata["source_role"] == "original"
    build = read(output / "original-build/RESULT.json")
    assert build["binaries"] == read(phase / "BINARY-PINS.json")
    assert build["native_sources"] == {name: row["candidate_sha256"] for name, row in read(here / "SOURCE-ROLES.json").items()}
    assert verify() == initial
    wpt.save(output / "PHASES-POST.json", initial)
    return result
