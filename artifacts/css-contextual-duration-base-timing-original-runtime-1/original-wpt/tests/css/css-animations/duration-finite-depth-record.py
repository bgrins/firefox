import json
import math
import os
from pathlib import Path
import re
import stat

FILES = {"depth-" + str(depth): "depth-" + str(depth) + ".json" for depth in (1, 2, 4, 8)}
PHASES = ["first-leaf-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"]


def numeric(value):
    return value is None or (type(value) in (int, float) and math.isfinite(value))


def timing(value):
    assert type(value) is dict and set(value) == {"duration", "progress", "time", "state"}
    assert numeric(value["duration"]) or type(value["duration"]) is str
    assert numeric(value["progress"]) and numeric(value["time"])
    assert type(value["state"]) is str


def snapshot(value, depth):
    assert type(value) is dict and set(value) == {"rootFont", "opacity", "leafDuration", "leaf", "nodes"}
    assert all(numeric(value[key]) for key in ("rootFont", "opacity", "leafDuration"))
    timing(value["leaf"])
    assert type(value["nodes"]) is list and len(value["nodes"]) == depth
    for node in value["nodes"]:
        assert type(node) is dict and set(node) == {"font", "lineHeight", "duration", "timing"}
        assert all(numeric(node[key]) for key in ("font", "lineHeight", "duration"))
        timing(node["timing"])


def validate(value):
    assert type(value) is dict and set(value) == {"kind", "observations"}
    kind = value["kind"]
    assert kind in FILES
    depth = int(kind.removeprefix("depth-"))
    observations = value["observations"]
    assert type(observations) is dict and set(observations) == {"literal", "contextual"}
    for mode, item in observations.items():
        assert type(item) is dict and set(item) == {"depth", "mode", "literalInitial", "initial", "samples", "beforeMembership", "membership", "afterMembership"}
        assert type(item["depth"]) is int and item["depth"] == depth and item["mode"] == mode
        for name in ("literalInitial", "initial", "beforeMembership", "afterMembership"):
            snapshot(item[name], depth)
        assert type(item["samples"]) is list and len(item["samples"]) == 4
        for sample, phase in zip(item["samples"], PHASES):
            assert type(sample) is dict and set(sample) == {"phase", "opacity"}
            assert sample["phase"] == phase and numeric(sample["opacity"])
        assert type(item["membership"]) is list and len(item["membership"]) == depth + 1
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
