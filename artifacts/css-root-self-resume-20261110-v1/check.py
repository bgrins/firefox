import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def observations(role):
    rows = {}
    for path in sorted((HERE / "historical" / role).glob("*.jsonl")):
        for line in path.read_text().splitlines():
            event = json.loads(line)
            if event["action"] not in ("test_status", "test_end"):
                continue
            key = (event["action"], event["test"], event.get("subtest"))
            assert key not in rows, key
            rows[key] = {
                field: event[field]
                for field in ("status", "message", "expected", "known_intermittent")
                if field in event
            }
    return rows


def main():
    for name, expected in json.loads((HERE / "FILES.json").read_text()).items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    selection = json.loads((HERE / "source-selection.json").read_text())["stage"]
    native = "servo/ports/geckolib/glue.rs"
    for role, expected in (
        ("original", selection["head_preimages"][native]),
        ("candidate", selection["files"][native]["sha256"]),
    ):
        build = json.loads(
            (HERE / "historical" / role / "build-result.json").read_text()
        )
        assert build["command_success"] and build["browser_build_performed"]
        assert build["native_sources"][native] == expected
    before, after = observations("original"), observations("candidate")
    assert before.keys() == after.keys()

    def counts(rows):
        return Counter((key[0], value["status"]) for key, value in rows.items())

    assert counts(before) == {
        ("test_status", "PASS"): 120,
        ("test_status", "FAIL"): 9,
        ("test_end", "OK"): 12,
    }
    assert counts(after) == {("test_status", "PASS"): 129, ("test_end", "OK"): 12}
    improvements = []
    for key, original in before.items():
        if original["status"] != "FAIL":
            assert after[key] == original, key
        else:
            assert (
                key[1] in selection["testharness_paths"]
                or "testing/web-platform/tests" + key[1]
                in selection["testharness_paths"]
            )
            improvements.append(key)
    print(
        json.dumps(
            {
                "historical_evidence_passed": True,
                "preserved_passes": 120,
                "candidate_passes": 129,
                "preserved_endings": 12,
                "improvements": improvements,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
