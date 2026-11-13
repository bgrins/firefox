import argparse
import base64
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def failures(path):
    report = json.loads(path.read_text())
    records = {}
    for test in report["results"]:
        if test["status"] == "FAIL":
            records[(test["test"], None)] = dict(message=test["message"], screenshots=test["screenshots"])
        for subtest in test["subtests"]:
            if subtest["status"] == "FAIL":
                records[(test["test"], subtest["name"])] = dict(message=subtest["message"])
    assert len(records) == 64
    return records


def authenticate_raw(path, expected):
    actual = {}
    pngs = []
    with path.open() as stream:
        for line in stream:
            event = json.loads(line)
            if event.get("status") != "FAIL" or event["action"] not in {"test_end", "test_status"}:
                continue
            key = (event["test"], event.get("subtest"))
            assert key not in actual
            detail = dict(message=event["message"])
            if event["action"] == "test_end":
                shots = {}
                for shot in event["extra"]["reftest_screenshots"]:
                    if not isinstance(shot, dict):
                        continue
                    data = base64.b64decode(shot["screenshot"], validate=True)
                    assert data.startswith(b"\x89PNG\r\n\x1a\n")
                    assert hashlib.sha1(data).hexdigest() == shot["hash"]
                    url = urlsplit(shot["url"])
                    name = url.path + ("?" + url.query if url.query else "")
                    assert name not in shots
                    shots[name] = "sha1:" + shot["hash"]
                    pngs.append(dict(test=event["test"], url=name,
                                     sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
                assert shots
                detail["screenshots"] = shots
            actual[key] = detail
    assert actual == expected, "Raw failure diagnostics or decoded PNG hashes differ from report"
    return pngs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["baseline", "candidate", "restored"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    artifacts = Path(__file__).resolve().parent.parent
    plan = artifacts / "css-grid-baseline-grid-bundle-validation-plan-20261112-v1"
    execution = artifacts / "css-grid-baseline-grid-bundle-validation-native-20261112-v1"
    assert file_hash(plan / "FILES.json") == "45e16af90418fd31582a27c84cdd3c6b766cf10322c3a2c2727679a8d1ea942d"
    expected = plan / "EXPECTED-ALIGNMENT.json"
    assert file_hash(expected) == json.loads((plan / "FILES.json").read_text())["files"][expected.name]["sha256"]
    report = execution / (args.phase + "-alignment-wptreport.json")
    raw = execution / (args.phase + "-alignment-raw.log")
    wanted, actual = failures(expected), failures(report)
    pngs = authenticate_raw(raw, actual)
    changes = [dict(test=key[0], subtest=key[1], expected=wanted.get(key), actual=actual.get(key))
               for key in sorted(wanted.keys() | actual.keys(), key=repr) if wanted.get(key) != actual.get(key)]
    record = dict(status="UNCHANGED_FAILURE_DETAILS" if not changes else "CHANGED_FAILURE_DETAILS",
                  phase=args.phase, file_failures=11, subtest_failures=53, changes=changes, pngs=pngs,
                  report_sha256=file_hash(report), raw_sha256=file_hash(raw),
                  reader_sha256=file_hash(Path(__file__).resolve()))
    with args.out.open("x") as output:
        json.dump(record, output, indent=2)
        output.write("\n")
    print(json.dumps(dict(status=record["status"], phase=args.phase, pngs=len(pngs), changes=len(changes))))
    raise SystemExit(bool(changes))


if __name__ == "__main__":
    main()
