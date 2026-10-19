import hashlib
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = here.parents[1]
source = here.parent / "css-tokenizer-string-comment-static-v1"
assert sys.argv[1:] in [["install"], ["remove"]]
for name in ["string-comment-controls.html", "known-badstring-recovery.html"]:
    original = (source / name).read_bytes()
    target = root / "testing/web-platform/tests/css/css-syntax" / name
    if sys.argv[1] == "install":
        assert not target.exists(), target
        target.write_bytes(original)
    else:
        assert target.read_bytes() == original, target
        target.unlink()
    print(sys.argv[1], name, hashlib.sha256(original).hexdigest())
