#!/usr/bin/env python3
"""Authenticate this research capsule; this is not a proof checker."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    assert digest(ROOT / "MANIFEST.json") == freeze["manifest_sha256"]
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    expected = set(manifest)
    actual = {
        str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()
    } - {"MANIFEST.json", "FREEZE.json"}
    assert actual == expected, (actual - expected, expected - actual)
    for name, sha in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert digest(ROOT / path) == sha, name
    for item in json.loads((ROOT / "LOCAL-INPUTS.json").read_text()):
        if "copy" in item:
            assert digest(ROOT / item["copy"]) == item["sha256"]
        else:
            assert digest(ROOT / item["excerpt"]) == item["excerpt_sha256"]
    results = {}
    for name, counts in [
        ("touching", {"FAIL": 1, "PASS": 4}),
        ("animation", {"FAIL": 2, "PASS": 4}),
    ]:
        receipt = json.loads((ROOT / "evidence" / (name + "-RUN.json")).read_text())
        assert receipt["stable_after"] is True
        assert Counter(row["status"] for row in receipt["rows"]) == counts
        identities = [(row["test"], row["subtest"]) for row in receipt["rows"]]
        assert len(identities) == len(set(identities))
        assert len(receipt["harness"]) == 1
        assert receipt["harness"][0]["status"] == "OK"
        assert len(receipt["suite_end_positions"]) == 1
        results[name] = counts
    report = (ROOT / "REPORT.md").read_text()
    assert all(f"## {i}." in report for i in range(1, 9))
    assert "not immutable full-page" in (ROOT / "SOURCES.json").read_text()
    print(json.dumps({"status": "PASS", "authenticated_inputs": len(manifest),
                      "historical_receipt_counts": results,
                      "scope": "Research integrity and retained receipt consistency only; no new proof or runtime."}, sort_keys=True))


if __name__ == "__main__":
    main()
