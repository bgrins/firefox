import json
import math
import os
from pathlib import Path
import re
import stat

FILES = {kind: kind + ".json" for kind in ("masked-base-acyclic",)}
PHASES = ["first-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"]


def numeric(value):
    return value is None or (type(value) in (int, float) and math.isfinite(value))


def timing(value):
    assert type(value) is dict and set(value) == {"duration", "progress", "time", "state"}
    assert numeric(value["duration"]) or type(value["duration"]) is str
    assert numeric(value["progress"]) and numeric(value["time"])
    assert type(value["state"]) is str


def snapshot(value, count):
    assert type(value) is dict and set(value) == {"font", "opacity", "cssDuration", "timings"}
    assert numeric(value["font"]) and numeric(value["opacity"])
    assert type(value["cssDuration"]) is str
    assert type(value["timings"]) is list and len(value["timings"]) == count
    for item in value["timings"]:
        timing(item)


def validate(value):
    assert type(value) is dict and set(value) == {"kind", "observations"}
    kind = value["kind"]
    assert kind in FILES
    acyclic = kind == "masked-base-acyclic"
    modes = ["contextual", "literal"] if acyclic else ["contextual", "literal500", "literal1000"]
    observations = value["observations"]
    assert type(observations) is dict and set(observations) == set(modes)
    count = 2 if acyclic else 1
    for mode in modes:
        item = observations[mode]
        assert type(item) is dict and set(item) == {"kind", "mode", "initial", "samples", "beforeMembership", "membership", "afterMembership"}
        assert item["kind"] == ("acyclic" if acyclic else "feedback") and item["mode"] == mode
        for name in ("initial", "beforeMembership", "afterMembership"):
            snapshot(item[name], count)
        assert type(item["samples"]) is list and len(item["samples"]) == 4
        for sample, phase in zip(item["samples"], PHASES):
            assert type(sample) is dict and set(sample) == {"phase", "value"}
            assert sample["phase"] == phase and numeric(sample["value"])
        assert type(item["membership"]) is list and len(item["membership"]) == count
        for member in item["membership"]:
            assert type(member) is dict and set(member) == {"animation", "effect"}
            assert all(type(flag) is bool for flag in member.values())
    return kind


def reject_constant(value):
    raise ValueError(value)


def main(request, response):
    assert request.method in ("POST", b"POST") and len(request.body) <= 65536
    value = json.loads(request.body, parse_constant=reject_constant)
    kind = validate(value)
    target = Path(os.environ["DURATION_PROGRESS_RECORD_DIR"])
    run_id = os.environ["DURATION_PROGRESS_RUN_ID"]
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
    acknowledgement = {"run_id": run_id, "kind": kind, "sampleCount": 4}
    return [(b"Content-Type", b"application/json"), (b"Cache-Control", b"no-store")], json.dumps(acknowledgement).encode()
