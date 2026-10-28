import json
import os
from pathlib import Path


def main(request, response):
    value = json.loads(request.body)
    assert value["caseCount"] == 24 and value["snapshotCount"] == len(value["snapshots"]) == 72
    target = Path(os.environ["ROUND_BASELINE_RECORD"])
    with target.open("x") as stream:
        json.dump(value, stream, indent=2)
    return [(b"Content-Type", b"text/plain")], b"recorded"
