import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def events(name):
    rows = [json.loads(line) for line in (HERE / name).read_text().splitlines()]
    assert sum(row["action"] == "suite_end" for row in rows) == 1, name
    statuses = {}
    endings = {}
    for row in rows:
        if row["action"] == "test_status":
            key = (row["test"], row["subtest"])
            assert key not in statuses, key
            statuses[key] = row["status"]
        elif row["action"] == "test_end":
            assert row["test"] not in endings, row["test"]
            endings[row["test"]] = row["status"]
    return statuses, endings


def main():
    for name, digest in read("FILES.json").items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    baseline, baseline_ends = events("baseline-raw.jsonl")
    controls, control_ends = events("controls-baseline-raw.jsonl")
    nightly, nightly_ends = events("installed-nightly-raw.jsonl")
    candidate, candidate_ends = events("candidate-raw.jsonl")
    assert collections.Counter(baseline.values()) == {"PASS": 4, "FAIL": 4}
    assert collections.Counter(controls.values()) == {"PASS": 39}
    assert nightly == baseline and nightly_ends == baseline_ends
    assert baseline.keys().isdisjoint(controls)
    original = baseline | controls
    assert candidate.keys() == original.keys()
    assert all(status == "PASS" for status in candidate.values())
    assert candidate_ends == baseline_ends | control_ends
    assert collections.Counter(candidate_ends.values()) == {"OK": 5, "PASS": 1}
    build = read("build-result.json")
    assert build["exit_code"] == 0
    assert build["source_hashes"] == read("candidate-source.json")
    assert build["test_hashes"] == read("baseline-before.json")["test_hashes"]
    assert read("candidate-result.json")["source_and_binary_hashes_match_build"]
    print(
        json.dumps(
            {
                "passed": True,
                "improvements": sum(status == "FAIL" for status in original.values()),
                "preserved_passes": sum(
                    status == "PASS" for status in original.values()
                ),
                "candidate_passes": len(candidate),
                "test_endings": candidate_ends,
                "scope": "Saved evidence integrity and callback comparison; no native execution or proof of source-to-binary correspondence",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
