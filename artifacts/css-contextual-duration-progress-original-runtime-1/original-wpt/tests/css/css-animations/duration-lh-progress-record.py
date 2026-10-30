import json
import math
import os
from pathlib import Path
import re
import stat

FILES = {f"lh-chain-{mode}": f"lh-chain-{mode}.json"
         for mode in ("literal", "ordinary", "animated")}
PHASES = ["first-child-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"]
TIMING = {"duration", "progress", "time", "state"}


def numeric(value):
    return value is None or (type(value) in (int, float) and math.isfinite(value))


def timing(value):
    assert isinstance(value, dict) and set(value) == TIMING
    assert all(numeric(value[key]) for key in ("progress", "time"))
    assert numeric(value["duration"]) or isinstance(value["duration"], str)
    assert isinstance(value["state"], str)


def snapshot(value):
    assert isinstance(value, dict) and set(value) == {
        "childOpacity", "childDuration", "childLineHeight", "child", "middleLineHeight",
        "middleDuration", "middle", "parentFont"}
    assert all(numeric(value[key]) for key in ("childOpacity", "childDuration", "childLineHeight", "middleLineHeight", "middleDuration", "parentFont"))
    timing(value["child"])
    timing(value["middle"])


def reject_constant(value):
    raise ValueError("Non-JSON numeric token: " + value)


def validate(value):
    assert isinstance(value, dict) and set(value) == {"kind", "observation"}
    kind = value["kind"]
    assert kind in FILES
    observation = value["observation"]
    assert isinstance(observation, dict) and set(observation) == {
        "mode", "samples", "beforeMembership", "driverTiming", "membership",
        "afterMembership", "seek751", "afterSeek"}
    assert observation["mode"] in ("literal", "ordinary", "animated")
    assert kind == "lh-chain-" + observation["mode"]
    samples = observation["samples"]
    assert isinstance(samples, list) and len(samples) == 4
    dimension = "opacity"
    for sample, phase in zip(samples, PHASES):
        assert isinstance(sample, dict) and set(sample) == {"phase", dimension}
        assert sample["phase"] == phase and numeric(sample[dimension])
    for name in ("beforeMembership", "afterMembership", "seek751", "afterSeek"):
        snapshot(observation[name])
    if observation["mode"] == "animated":
        timing(observation["driverTiming"])
    else:
        assert observation["driverTiming"] is None
    flags = observation["membership"]
    assert isinstance(flags, dict) and set(flags) == {"middle", "child", "middleEffect", "childEffect"}
    assert all(type(flag) is bool for flag in flags.values())
    return kind


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
