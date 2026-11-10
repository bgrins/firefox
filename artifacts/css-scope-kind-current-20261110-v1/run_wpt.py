import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    role, binary = sys.argv[1:]
    assert role in {"installed-nightly", "candidate"}
    binary = Path(binary).resolve()
    app = binary.parent.parent
    paths = [binary, binary.parent / "XUL", app / "Resources/application.ini"]
    before = {str(path): digest(path) for path in paths}
    tests = [
        "css/css-cascade/implicit-scope-cache-index.html",
        "css/css-cascade/implicit-scope-root-kind.html",
        "css/css-conditional/shared-sheet-media.html",
        "css/css-conditional/shared-sheet-media-history.html",
    ]
    command = [
        "/Users/bgrins/venvs/firefox/bin/python",
        "./mach",
        "wpt",
        "--headless",
        "--processes=1",
        "--no-manifest-update",
        "--no-manifest-download",
        "--no-install-fonts",
        "--no-enable-webtransport-h3",
        f"--binary={binary}",
        f"--log-raw={HERE / (role + '-raw.jsonl')}",
        *["testing/web-platform/tests/" + test for test in tests],
    ]
    resources = json.loads((HERE / "baseline-before.json").read_text())["test_hashes"]
    for path, expected in resources.items():
        assert digest(ROOT / path) == expected, path
    source_before = digest(ROOT / "servo/components/style/stylist.rs")
    (HERE / (role + "-before.json")).write_text(
        json.dumps({"binaries": before, "command": command}, indent=2) + "\n"
    )
    with (HERE / (role + "-wpt.log")).open("w") as log:
        process = subprocess.run(
            command,
            cwd=ROOT,
            env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1"),
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    after = {str(path): digest(path) for path in paths}
    result = {
        "exit_code": process.returncode,
        "before": before,
        "after": after,
        "binaries_unchanged": before == after,
        "source_before": source_before,
        "source_after": digest(ROOT / "servo/components/style/stylist.rs"),
    }
    (HERE / (role + "-result.json")).write_text(json.dumps(result, indent=2) + "\n")
    assert before == after
    for path, expected in resources.items():
        assert digest(ROOT / path) == expected, path
    print(json.dumps(result, indent=2))
    sys.exit(process.returncode)


if __name__ == "__main__":
    main()
