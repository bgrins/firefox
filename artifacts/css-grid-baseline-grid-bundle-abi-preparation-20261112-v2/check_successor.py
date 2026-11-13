import json
import shutil
import tempfile
from pathlib import Path

import run

HERE = Path(__file__).resolve().parent


def main():
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text())
    old = Path(predecessor["preparation"])
    assert run.sha(old / "FILES.json") == predecessor["manifest_sha256"]
    for name, row in json.loads((old / "FILES.json").read_text())["files"].items():
        assert run.sha(old / name) == row["sha256"]
    old_pins = json.loads((old / "INPUTS.json").read_text())
    pins = json.loads((HERE / "INPUTS.json").read_text())
    assert all(pins[name] == row for name, row in old_pins.items())
    review = json.loads((HERE / "BASELINE-DEPENDENCIES-REVIEW.json").read_text())
    assert review["count"] == len(review["dependencies"]) == 2296
    assert len(review["explicit_alias_additions"]) == 2
    for row in review["explicit_alias_additions"]:
        path = Path(row["alias"])
        assert str(path.readlink()) == row["link_text"]
        assert str(path.resolve()) == row["resolved"]
        assert run.sha(path) == row["sha256"]
        assert row["alias"] not in old_pins
        assert row["prior_pinned_paths"]
        for original in row["prior_pinned_paths"]:
            assert old_pins[original] == pins[row["alias"]]
    expected_new = {row["alias"] for row in review["explicit_alias_additions"]}
    expected_new.add(str(old / "FILES.json"))
    execution = Path(predecessor["execution"])
    expected_new.update(str(execution / name) for name in (
        "PREPARATION.json", "baseline.d", "baseline.stdout", "baseline.stderr",
        "baseline-COMMAND.json", "RESULT.json"))
    assert set(pins) - set(old_pins) == expected_new
    for name in ("run.py", "lifecycle.py", "layouts.py", "check.py", "baseline-probe.inc", "candidate-probe.inc"):
        assert (HERE / name).read_bytes() == (old / name).read_bytes()
    for name in ("REQUESTS.json", "baseline-overlay.json", "candidate-overlay.json"):
        assert (HERE / name).read_text() == (old / name).read_text().replace(str(old), str(HERE))
    request = json.loads((HERE / "REQUESTS.json").read_text())[0]
    with tempfile.TemporaryDirectory(prefix="grid-abi-alias-review-") as tmp:
        scratch = Path(tmp)
        shutil.copyfile(HERE / "OBSERVED-BASELINE.d", scratch / "baseline.d")
        run.dependencies(request, scratch, pins)
        data = json.loads((scratch / "baseline-DEPENDENCIES.json").read_text())
        assert len(data) == 2296
        assert set(data) == set(review["dependencies"])
        for name, row in review["dependencies"].items():
            expected = row["effective_baseline_overlay"] or name
            assert data[name]["effective_source"] == expected
            assert data[name]["sha256"] == run.sha(Path(expected))
    assert not scratch.exists()
    result = dict(status="PASS exact alias successor and complete retained baseline dependency reconciliation",
                  old_pins_preserved=len(old_pins), total_pins=len(pins),
                  explicit_aliases=2, observed_dependencies=2296,
                  runner_lifecycle_parser_commands_unchanged_except_paths=True,
                  compiler_executed=False, scratch_removed=True)
    (HERE / "SUCCESSOR-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
