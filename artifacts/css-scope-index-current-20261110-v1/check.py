import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(name):
    return json.loads((HERE / name).read_text())


def events(name):
    rows = [json.loads(line) for line in (HERE / name).read_text().splitlines()]
    assert sum(row["action"] == "suite_end" for row in rows) == 1
    statuses, endings = {}, {}
    for row in rows:
        if row["action"] == "test_status":
            key = (row["test"], row["subtest"])
            assert key not in statuses
            statuses[key] = (row["status"], row.get("message"))
        elif row["action"] == "test_end":
            assert row["test"] not in endings
            endings[row["test"]] = row["status"]
    return statuses, endings


def main():
    for name, digest in read("FILES.json").items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    baseline, ends = events("baseline-raw.jsonl")
    candidate, candidate_ends = events("candidate-raw.jsonl")
    nightly, nightly_ends = events("installed-nightly-raw.jsonl")
    assert baseline.keys() == candidate.keys() == nightly.keys()
    assert ends == candidate_ends == nightly_ends
    assert collections.Counter(ends.values()) == {"OK": 4}
    assert collections.Counter(status for status, _ in baseline.values()) == {
        "PASS": 10,
        "FAIL": 4,
    }
    assert collections.Counter(status for status, _ in candidate.values()) == {
        "PASS": 12,
        "FAIL": 2,
    }
    assert collections.Counter(status for status, _ in nightly.values()) == {
        "PASS": 6,
        "FAIL": 8,
    }
    changed = []
    for key, value in baseline.items():
        if candidate[key] != value:
            assert key[0].endswith("implicit-scope-cache-index.html")
            assert value[0] == "FAIL" and candidate[key][0] == "PASS"
            changed.append(key)
        if "/css-cascade/" in key[0]:
            assert nightly[key] == value
    assert len(changed) == 2
    build = read("build-result.json")
    result = read("candidate-result.json")
    assert build["exit_code"] == 0 and result["exit_code"] == 1
    assert build["test_hashes"] == read("baseline-before.json")["test_hashes"]
    assert (
        result["source_before"]
        == result["source_after"]
        == build["source_hashes"]["servo/components/style/stylist.rs"]
    )
    assert (
        result["before"]
        == result["after"]
        == {str(ROOT / path): digest for path, digest in build["binaries"].items()}
    )
    assert read("installed-nightly-result.json")["binaries_unchanged"]
    proof = read("lean-replay/RESULT.json")
    assert (
        proof["passed"]
        and len(proof["theorems"]) == 34
        and len(proof["false_controls"]) == 12
    )
    print(
        json.dumps(
            {
                "passed": True,
                "improvements": changed,
                "preserved_passes": 10,
                "remaining_host_context_failures": 2,
                "scope": "Saved evidence integrity and callback comparison; no new browser execution",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
