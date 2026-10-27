import json, os, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEAN = (
    BASE.parents[1]
    / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
)
MUTATIONS = {
    "UnguardedFirst": (
        "match guardedLookup cache candidate.source candidate.side with",
        "match unguardedLookup cache candidate.source candidate.side with",
    ),
    "UnguardedSecond": (
        "(guardedLookup populated candidate.source candidate.side, populated)",
        "(unguardedLookup populated candidate.source candidate.side, populated)",
    ),
    "WrongStoredIdentity": (
        "some (source.identity, value)",
        "some (source.shorthand, value)",
    ),
}
if __name__ == "__main__":
    out = BASE / "controls-discovery-v1"
    out.mkdir()
    model = (BASE / "Provenance.lean").read_text()
    for name, (old, new) in MUTATIONS.items():
        if model.count(old) != 1:
            raise RuntimeError(name)
        d = out / name
        d.mkdir()
        p = d / "Provenance.lean"
        p.write_text(model.replace(old, new))
        env = os.environ.copy()
        env["LEAN_PATH"] = str(d)
        env.pop("LEAN_SRC_PATH", None)
        command = [str(LEAN), "-DwarningAsError=true", str(p)]
        r = subprocess.run(command, cwd=d, env=env, capture_output=True, text=True)
        (d / "stdout").write_text(r.stdout)
        (d / "stderr").write_text(r.stderr)
        (d / "command.json").write_text(
            json.dumps(
                {"command": command, "cwd": str(d), "exit": r.returncode}, indent=2
            )
            + "\n"
        )
        print(name, r.returncode, r.stdout)
