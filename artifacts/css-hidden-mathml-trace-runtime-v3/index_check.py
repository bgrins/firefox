import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def index_state(wpt, verify_payloads=True):
    expected = json.loads((HERE / "INDEX-EXPECTATIONS.json").read_text())
    paths = wpt.git("diff", "--cached", "--name-only").decode().splitlines()
    need(sorted(paths) == expected["staged_paths"] and len(paths) == 925,
         "staged research path roster changed")
    need(set(paths) == set(expected["staged_payload_sha256"])
         and all(name.startswith("artifacts/") and "\n" not in name
                 and "\0" not in name for name in paths), "invalid staged role")
    need(wpt.git("rev-parse", "HEAD").decode().strip() == expected["head"], "HEAD changed")
    need(hashlib.sha256(wpt.git("diff", "--cached", "--binary")).hexdigest()
         == expected["index_diff_sha256"], "staged diff changed")
    need(hashlib.sha256(wpt.git("ls-files", "--stage", "-z")).hexdigest()
         == expected["index_entries_sha256"], "index entries changed")
    if verify_payloads:
        import subprocess
        data = subprocess.check_output(wpt.GIT + ["cat-file", "--batch"],
            input="".join(":" + name + "\n" for name in paths).encode(),
            cwd=ROOT, env=wpt.ENV)
        offset = 0
        for name in paths:
            end = data.index(b"\n", offset)
            header = data[offset:end].split()
            need(len(header) == 3 and header[1] == b"blob", "staged blob missing " + name)
            size = int(header[2])
            offset = end + 1
            body = data[offset:offset + size]
            need(len(body) == size and hashlib.sha256(body).hexdigest()
                 == expected["staged_payload_sha256"][name], "staged payload changed " + name)
            offset += size
            need(data[offset:offset + 1] == b"\n", "invalid batch delimiter")
            offset += 1
        need(offset == len(data), "extra staged batch output")
    return expected

