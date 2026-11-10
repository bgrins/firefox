import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Use python3 -I without -O")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, record in sources.items():
        data = (HERE / "source" / path).read_bytes()
        assert digest(data) == record["sha256"], path
        pinned = subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", "show", record["revision"] + ":" + path],
            cwd=ROOT,
        )
        assert data == pinned, path
    excerpts = json.loads((HERE / "EXCERPTS.json").read_text())
    for record in excerpts:
        lines = (HERE / "source" / record["path"]).read_text().splitlines(keepends=True)
        text = "".join(lines[record["first"] - 1 : record["last"]])
        assert text == record["text"], record["path"]
        assert digest(text.encode()) == record["sha256"]
    specs = json.loads((HERE / "SPEC-SNAPSHOTS.json").read_text())
    for record in specs:
        data = (HERE / record["name"]).read_bytes()
        assert digest(data) == record["sha256"], record["name"]
        text = " ".join(html.unescape(re.sub("<[^>]+>", " ", data.decode())).split())
        if record["name"] == "variables-2015.html":
            assert "used in the animation property or one of its longhands" in text
        else:
            assert "used in a property that is not animatable" in text
        if record["name"] == "variables-current.html":
            assert "second arg was provided" in text
        else:
            assert "Otherwise, if the var() function has a fallback value" in text
    output = HERE / sys.argv[1]
    assert not output.exists()
    output.write_text(json.dumps({
        "source_files": len(sources),
        "pinned_git_bytes_match": True,
        "authenticated_excerpts": len(excerpts),
        "authenticated_spec_snapshots": len(specs),
        "history": "2015 animation-properties-only; 2021, 2022 and current all nonanimatable properties",
        "browser_execution": False,
        "semantic_proof": False,
        "checker_sha256": digest(Path(__file__).read_bytes()),
    }, indent=2) + "\n")
    print(f"Authenticated {len(sources)} source files, {len(excerpts)} excerpts and {len(specs)} spec snapshots")


if __name__ == "__main__":
    main()
