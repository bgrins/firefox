import argparse
import json
import subprocess


def git(*args, data=None):
    return subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args],
        input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def main():
    parser = argparse.ArgumentParser(description="Check all blobs introduced by a Git history range, including files deleted at its tip.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--tip", default="HEAD")
    parser.add_argument("--warn-bytes", type=int, default=50 * 1024**2)
    parser.add_argument("--max-bytes", type=int, default=100 * 1024**2)
    args = parser.parse_args()
    if not 0 < args.warn_bytes <= args.max_bytes:
        parser.error("Require 0 < warn-bytes <= max-bytes")
    base = git("rev-parse", "--verify", "--end-of-options", args.base + "^{commit}").decode().strip()
    tip = git("rev-parse", "--verify", "--end-of-options", args.tip + "^{commit}").decode().strip()
    objects = git("rev-list", "--objects", base + ".." + tip)
    sizes = git("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)", data=objects)
    warnings, errors, largest, count = [], [], None, 0
    for line in sizes.decode().splitlines():
        oid, kind, size, *path = line.split(" ", 3)
        if kind != "blob":
            continue
        row = dict(oid=oid, bytes=int(size), path=path[0] if path else None)
        count += 1
        if largest is None or row["bytes"] > largest["bytes"]:
            largest = row
        if row["bytes"] > args.warn_bytes:
            warnings.append(row)
        if row["bytes"] > args.max_bytes:
            errors.append(row)
    print(json.dumps(dict(base=base, tip=tip, blobs=count, largest=largest,
                          warnings=warnings, errors=errors,
                          status="FAIL" if errors else "PASS"), indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
