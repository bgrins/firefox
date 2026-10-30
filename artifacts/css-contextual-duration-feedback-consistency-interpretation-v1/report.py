import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values(snapshot):
    return {key: snapshot[key] for key in ("style", "effects")}


def summarize_read(snapshot):
    differences = {}
    for primary, repeated in (
        ("style", "repeatStyle"),
        ("style", "afterMembershipStyle"),
        ("effects", "repeatEffects"),
        ("effects", "currentEffects"),
    ):
        if snapshot[primary] != snapshot[repeated]:
            differences[repeated] = snapshot[repeated]
    return dict(
        values(snapshot),
        order=snapshot["order"],
        sameAnimations=snapshot["sameAnimations"],
        sameEffects=snapshot["sameEffects"],
        read_differences=differences,
    )


def summarize_record(record):
    trajectories = []
    for trajectory in record["trajectories"]:
        phases = []
        for phase in trajectory["phases"]:
            first, second = phase["reads"]
            phases.append({
                "name": phase["name"],
                "reads": [summarize_read(first), summarize_read(second)],
                "primary_values_equal_between_read_orders": values(first) == values(second),
            })
        trajectories.append({
            "role": trajectory["role"],
            "acquisition": {
                key: summarize_read(snapshot)
                for key, snapshot in trajectory["acquisition"].items()
            },
            "phases": phases,
        })
    return {"kind": record["kind"], "trajectories": trajectories}


def summarize_runtime(directory, manifest_sha256):
    directory = Path(directory)
    assert digest(directory / "FILES.json") == manifest_sha256
    manifest = read(directory / "FILES.json")
    for name, expected in manifest.items():
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert digest(directory / relative) == expected, name
    required = [
        "ROOT-TERMINAL.json", "feedback-wpt/ASSESSMENT.json",
        "feedback-records/coupled.json", "feedback-records/zero-start.json",
    ]
    assert all(name in manifest for name in required)
    terminal = read(directory / "ROOT-TERMINAL.json")
    assessment = read(directory / "feedback-wpt/ASSESSMENT.json")
    receipt_path = directory / "FEEDBACK-RECORDS.json"
    receipt = read(receipt_path) if "FEEDBACK-RECORDS.json" in manifest else None
    return {
        "directory": str(directory),
        "manifest_sha256": manifest_sha256,
        "terminal": terminal,
        "complete": assessment["complete"],
        "callback_results": [{key: row.get(key) for key in ("subtest", "status", "message")}
                             for row in assessment["rows"]],
        "record_receipt": receipt,
        "records": [summarize_record(read(directory / name)) for name in required[2:]],
    }


def compare(original, candidate):
    changes = []
    for old_record, new_record in zip(original["records"], candidate["records"], strict=True):
        assert old_record["kind"] == new_record["kind"]
        for old, new in zip(old_record["trajectories"], new_record["trajectories"], strict=True):
            assert old["role"] == new["role"]
            for key in old["acquisition"]:
                if old["acquisition"][key] != new["acquisition"][key]:
                    changes.append({"kind": old_record["kind"], "role": old["role"],
                                    "stage": key, "original": old["acquisition"][key],
                                    "candidate": new["acquisition"][key]})
            for before, after in zip(old["phases"], new["phases"], strict=True):
                assert before["name"] == after["name"]
                if before != after:
                    changes.append({"kind": old_record["kind"], "role": old["role"],
                                    "stage": before["name"], "original": before,
                                    "candidate": after})
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", nargs=2, metavar=("DIRECTORY", "MANIFEST_SHA256"), required=True)
    parser.add_argument("--candidate", nargs=2, metavar=("DIRECTORY", "MANIFEST_SHA256"))
    args = parser.parse_args()
    report = {
        "original": summarize_runtime(*args.original),
        "limits": [
            "Callback PASS certifies the authored acquisition and fixed literal/override controls.",
            "Self-dependent values and membership are measurements, not a fixed-point oracle.",
            "Getters are sequential and getAnimations can flush; equal reads do not prove atomicity.",
            "The report does not infer a native scheduling sequence, cycle, hang or convergence.",
        ],
    }
    if args.candidate:
        report["candidate"] = summarize_runtime(*args.candidate)
        report["observed_changes"] = compare(report["original"], report["candidate"])
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
