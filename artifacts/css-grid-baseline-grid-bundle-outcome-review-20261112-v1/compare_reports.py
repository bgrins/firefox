import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def report_rows(path):
    report = json.loads(path.read_text())
    rows = []
    for test in report["results"]:
        prefix = (test.get("subsuite", ""), test["test"])
        rows.append((*prefix, None, test["status"]))
        rows.extend((*prefix, sub["name"], sub["status"]) for sub in test["subtests"])
    assert len({row[:3] for row in rows}) == len(rows), (path, "duplicate identity")
    return Counter(rows)


def raw_rows(path):
    rows = []
    starts = Counter()
    ends = Counter()
    actions = Counter()
    with path.open() as stream:
        for line in stream:
            event = json.loads(line)
            action = event["action"]
            actions[action] += 1
            if action not in {"test_start", "test_end", "test_status"}:
                continue
            prefix = (event.get("subsuite", ""), event["test"])
            if action == "test_start":
                starts[prefix] += 1
            else:
                subtest = event["subtest"] if action == "test_status" else None
                rows.append((*prefix, subtest, event["status"]))
                if action == "test_end":
                    ends[prefix] += 1
    assert actions["suite_start"] == actions["suite_end"] == 1, path
    assert starts == ends and all(count == 1 for count in starts.values()), path
    assert len({row[:3] for row in rows}) == len(rows), (path, "duplicate identity")
    return Counter(rows), dict(actions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", action="append", required=True,
                        choices=["baseline", "candidate", "restored"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    assert len(args.phase) == len(set(args.phase))
    artifacts = Path(__file__).resolve().parent.parent
    plan = artifacts / "css-grid-baseline-grid-bundle-validation-plan-20261112-v1"
    execution = artifacts / "css-grid-baseline-grid-bundle-validation-native-20261112-v1"
    assert digest(plan / "FILES.json") == "45e16af90418fd31582a27c84cdd3c6b766cf10322c3a2c2727679a8d1ea942d"
    pins = json.loads((plan / "FILES.json").read_text())["files"]
    results = {}
    for suite, expected_files, expected_subtests in [("focused", 3, 700), ("alignment", 457, 2490)]:
        expected = plan / ("EXPECTED-" + suite.upper() + ".json")
        assert digest(expected) == pins[expected.name]["sha256"]
        wanted = report_rows(expected)
        file_counts = Counter(row[3] for row in wanted if row[2] is None)
        sub_counts = Counter(row[3] for row in wanted if row[2] is not None)
        assert sum(file_counts.values()) == expected_files
        assert sum(sub_counts.values()) == expected_subtests
        if suite == "focused":
            assert file_counts == {"OK": 3} and sub_counts == {"PASS": 700}
        else:
            assert file_counts["FAIL"] == 11 and sub_counts["FAIL"] == 53
        for phase in args.phase:
            label = phase + "-" + suite
            report = execution / (label + "-wptreport.json")
            raw = execution / (label + "-raw.log")
            actual = report_rows(report)
            events, actions = raw_rows(raw)
            assert actual == wanted, (label, "report differs from preserved outcomes")
            assert events == actual, (label, "raw events differ from report")
            results[label] = dict(files=expected_files, subtests=expected_subtests,
                                  file_statuses=dict(file_counts), subtest_statuses=dict(sub_counts),
                                  report_sha256=digest(report), raw_sha256=digest(raw), actions=actions)
    record = dict(status="EXACT_OUTCOMES_AND_RAW_EVENTS_MATCH", phases=args.phase,
                  scope="Test outcomes only; source, binary, process and restoration acceptance are separate",
                  results=results, reader_sha256=digest(Path(__file__).resolve()))
    with args.out.open("x") as output:
        json.dump(record, output, indent=2)
        output.write("\n")
    print(json.dumps(dict(status=record["status"], phases=args.phase, reports=len(results))))


if __name__ == "__main__":
    main()
