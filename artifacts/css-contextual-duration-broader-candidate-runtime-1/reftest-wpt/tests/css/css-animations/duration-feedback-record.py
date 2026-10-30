import json
import os
from pathlib import Path
import re
import stat

FILES = {"self font": "self.json", "coupled font and opacity": "coupled.json",
         "zero-start self font": "zero-start.json"}
SAMPLE_KEYS = {"font", "cssDuration", "opacity", "effects", "repeatFont", "repeatDuration"}
EFFECT_KEYS = {"name", "time", "duration", "progress", "state"}


def number_or_null(value):
    return value is None or type(value) in (int, float)


def reject_constant(value):
    raise ValueError("Non-JSON numeric token: " + value)


def main(request, response):
    assert request.method in ("POST", b"POST")
    assert len(request.body) <= 65536
    value = json.loads(request.body, parse_constant=reject_constant)
    assert isinstance(value, dict) and set(value) == {"kind", "samples"}
    kind = value["kind"]
    assert kind in FILES
    samples = value["samples"]
    assert isinstance(samples, list) and len(samples) == 8
    for sample in samples:
        assert isinstance(sample, dict) and set(sample) == SAMPLE_KEYS
        assert all(isinstance(sample[key], str) for key in SAMPLE_KEYS - {"effects"})
        effects = sample["effects"]
        assert isinstance(effects, list) and len(effects) == (2 if kind == "coupled font and opacity" else 1)
        for effect in effects:
            assert isinstance(effect, dict) and set(effect) == EFFECT_KEYS
            assert isinstance(effect["name"], str) and isinstance(effect["state"], str)
            assert number_or_null(effect["time"]) and number_or_null(effect["progress"])
            assert number_or_null(effect["duration"]) or isinstance(effect["duration"], str)
    target = Path(os.environ["DURATION_FEEDBACK_RECORD_DIR"])
    run_id = os.environ["DURATION_FEEDBACK_RUN_ID"]
    assert target.is_absolute()
    assert re.fullmatch(r"[A-Za-z0-9_-]{16,128}", run_id)
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
    acknowledgement = {"run_id": run_id, "kind": kind, "sampleCount": len(samples)}
    return [(b"Content-Type", b"application/json"), (b"Cache-Control", b"no-store")], json.dumps(acknowledgement).encode()
