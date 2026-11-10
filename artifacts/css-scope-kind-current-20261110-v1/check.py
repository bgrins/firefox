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
            statuses[key] = row["status"]
        elif row["action"] == "test_end":
            assert row["test"] not in endings
            endings[row["test"]] = row["status"]
    return statuses, endings


def main():
    for name, expected in read("FILES.json").items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected
    for record in read("REFERENCES.json").values():
        assert (
            hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
            == record["sha256"]
        )
    baseline, ends = events("baseline-raw.jsonl")
    candidate, candidate_ends = events("candidate-raw.jsonl")
    assert baseline.keys() == candidate.keys()
    assert ends == candidate_ends and collections.Counter(ends.values()) == {"OK": 4}
    assert collections.Counter(baseline.values()) == {"PASS": 12, "FAIL": 2}
    assert collections.Counter(candidate.values()) == {"PASS": 14}
    improved = [key for key in baseline if baseline[key] == "FAIL"]
    assert all(key[0].endswith("implicit-scope-root-kind.html") for key in improved)
    build = read("build-result.json")
    result = read("candidate-result.json")
    assert build["exit_code"] == result["exit_code"] == 0
    assert build["test_hashes"] == read("baseline-before.json")["test_hashes"]
    assert (
        result["source_before"]
        == result["source_after"]
        == build["source_hashes"]["servo/components/style/stylist.rs"]
    )
    assert (
        result["before"]
        == result["after"]
        == {str(ROOT / path): expected for path, expected in build["binaries"].items()}
    )
    print(
        json.dumps(
            {
                "passed": True,
                "improvements": improved,
                "preserved_passes": 12,
                "candidate_passes": 14,
                "scope": "Saved evidence comparison; baseline explicitly reused from the preceding index run",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
