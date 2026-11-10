import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec-root", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads((ROOT / "SOURCES.json").read_text())["sources"]
    clauses = json.loads((ROOT / "CLAUSES.json").read_text())["clauses"]
    checked = {}
    for clause in clauses:
        source = sources[clause["source"]]
        data = (args.spec_root / source["file"]).read_bytes()
        if sha(data) != source["sha256"]:
            raise ValueError("Original snapshot drift: " + clause["source"])
        excerpt = data[clause["start"]:clause["end"]]
        if sha(excerpt) != clause["sha256"] or excerpt != (ROOT / clause["file"]).read_bytes():
            raise ValueError("Original span mismatch: " + clause["anchor"])
        checked[clause["source"]] = source["sha256"]
    library = json.loads((ROOT / "LIBRARY.json").read_text())
    for name, digest in library["sha256"].items():
        result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(args.library),
                                 "show", library["revision"] + ":" + name], capture_output=True)
        if result.returncode or sha(result.stdout) != digest or result.stdout != (ROOT / name).read_bytes():
            raise ValueError("Pinned library mismatch: " + name)
    report = {"status": "pass", "full_snapshot_sha256": checked, "excerpt_count": len(clauses),
              "library_revision": library["revision"], "library_git_objects_matched": True}
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print("Origins authenticated: nine exact source spans and four pinned library modules")


if __name__ == "__main__":
    main()
