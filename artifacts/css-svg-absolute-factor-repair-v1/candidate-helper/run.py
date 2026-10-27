import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


command = [
    "clang++", "-std=c++20", "-O1", "-g", "-fsanitize=undefined,integer",
    "-fno-sanitize-recover=all", "-DMOZILLA_INTERNAL_API", "-I",
    "objdir-full.noindex/dist/include", "-I",
    "objdir-full.noindex/dist/include/nspr", "-include",
    "objdir-full.noindex/mozilla-config.h", "-MMD", "-MF",
    str(HERE / "helper.d"), str(HERE / "helper.cpp"), "-o", str(HERE / "helper"),
]
record = {"command": command, "source_pins_sha256": sha(HERE / "SOURCE-PINS.json")}
products = [HERE / "helper", HERE / "helper.d", HERE / "helper.dSYM"]
assert all(not p.exists() for p in products)
pins = json.loads((HERE / "SOURCE-PINS.json").read_text())["sources"]
assert all(sha(ROOT / path) == value for path, value in pins.items())
try:
    with (HERE / "compile.log").open("w") as log:
        record["compile_exit"] = subprocess.run(
            command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=60
        ).returncode
    assert record["compile_exit"] == 0
    dep = (HERE / "helper.d").read_text().replace("\\\n", " ")
    record["dependencies"] = {
        name: sha(ROOT / name) for name in dep.split(":", 1)[1].split()
    }
    record["binary_sha256"] = sha(HERE / "helper")
    with (HERE / "stdout.log").open("w") as out, (HERE / "stderr.log").open("w") as err:
        process = subprocess.Popen(
            [str(HERE / "helper")], cwd=ROOT, stdout=out, stderr=err,
            start_new_session=True,
        )
        record["pid"] = process.pid
        try:
            record["run_exit"] = process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            record["timeout"] = True
            os.killpg(process.pid, signal.SIGKILL)
            record["run_exit"] = process.wait()
    assert record["run_exit"] == 0
    assert not (HERE / "stderr.log").read_bytes()
    rows = [json.loads(line) for line in (HERE / "stdout.log").read_text().splitlines()]
    oracle = json.loads((HERE / "ORACLE.json").read_text())["rows"]
    assert [(r["target"], r["source"]) for r in rows] == [
        (r["target"], r["source"]) for r in oracle
    ]
    record["rows"] = len(rows)
    record["mismatches"] = [row for row in rows if not row["match"]]
    record["predicate_inputs"] = 65536
    record["number_alias_checks"] = 15
finally:
    record["source_preserved"] = all(sha(ROOT / path) == value for path, value in pins.items())
    record["removed_products"] = {
        str(f.relative_to(HERE)): sha(f)
        for p in products
        for f in (sorted(p.rglob("*")) if p.is_dir() else [p])
        if f.is_file()
    }
    for p in products:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    record["products_absent"] = all(not p.exists() for p in products)
    save("CHECK.json", record)
print(json.dumps({k: record[k] for k in ["compile_exit", "run_exit", "rows", "mismatches", "products_absent"]}, indent=2))
