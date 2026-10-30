import json
import os
from pathlib import Path
import re
import stat

FILES = {"coupled": "coupled.json", "zero-start": "zero-start.json"}
ROLES = ["passive", "seek", "outline", "override", "literal"]
PHASES = ["initial-750", "action-751", "return-750", "repeat-750"]
STYLE = {"font", "cssDuration", "opacity", "outlineWidth"}
EFFECT = {"name", "time", "duration", "progress", "state"}
READ = {"order", "style", "effects", "repeatEffects", "repeatStyle",
        "sameAnimations", "sameEffects", "currentEffects", "afterMembershipStyle"}


def numeric(value):
    return value is None or type(value) in (int, float)


def effects(values, count=None):
    assert isinstance(values, list)
    assert (len(values) == count) if count is not None else (len(values) <= 8)
    for effect in values:
        assert isinstance(effect, dict) and set(effect) == EFFECT
        assert isinstance(effect["name"], str) and isinstance(effect["state"], str)
        assert numeric(effect["time"]) and numeric(effect["progress"])
        assert numeric(effect["duration"]) or isinstance(effect["duration"], str)


def reading(value, count):
    assert isinstance(value, dict) and set(value) == READ
    assert value["order"] in ("style-first", "timing-first")
    for key in ("style", "repeatStyle", "afterMembershipStyle"):
        assert isinstance(value[key], dict) and set(value[key]) == STYLE
        assert all(isinstance(item, str) for item in value[key].values())
    for key in ("effects", "repeatEffects"):
        effects(value[key], count)
    effects(value["currentEffects"])
    for key in ("sameAnimations", "sameEffects"):
        assert isinstance(value[key], list) and len(value[key]) == count
        assert all(type(item) is bool for item in value[key])


def reject_constant(value):
    raise ValueError("Non-JSON numeric token: " + value)


def validate(value):
    assert isinstance(value, dict) and set(value) == {"kind", "trajectories"}
    kind = value["kind"]
    assert kind in FILES
    count = 2 if kind == "coupled" else 1
    trajectories = value["trajectories"]
    assert isinstance(trajectories, list) and [item["role"] for item in trajectories] == ROLES
    for trajectory in trajectories:
        assert set(trajectory) == {"role", "acquisition", "phases"}
        acquisition = trajectory["acquisition"]
        assert isinstance(acquisition, dict) and set(acquisition) == {"beforeReady", "afterReady"}
        for sample in acquisition.values():
            assert sample["order"] == "timing-first"
            reading(sample, count)
        phases = trajectory["phases"]
        assert isinstance(phases, list) and [phase["name"] for phase in phases] == PHASES
        for index, phase in enumerate(phases):
            assert set(phase) == {"name", "reads"} and isinstance(phase["reads"], list)
            assert [sample["order"] for sample in phase["reads"]] == (
                ["timing-first", "style-first"] if index % 2 else ["style-first", "timing-first"])
            for sample in phase["reads"]:
                reading(sample, count)
    return kind


def main(request, response):
    assert request.method in ("POST", b"POST") and len(request.body) <= 65536
    value = json.loads(request.body, parse_constant=reject_constant)
    kind = validate(value)
    target = Path(os.environ["DURATION_FEEDBACK_RECORD_DIR"])
    run_id = os.environ["DURATION_FEEDBACK_RUN_ID"]
    assert target.is_absolute() and re.fullmatch(r"[A-Za-z0-9_-]{16,128}", run_id)
    directory = os.open(target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(directory)
        assert info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700
        descriptor = os.open(FILES[kind], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        with os.fdopen(descriptor, "w") as stream:
            json.dump({"run_id": run_id, **value}, stream, indent=2, allow_nan=False)
    finally:
        os.close(directory)
    acknowledgement = {"run_id": run_id, "kind": kind, "sampleCount": 20}
    return [(b"Content-Type", b"application/json"), (b"Cache-Control", b"no-store")], json.dumps(acknowledgement).encode()
