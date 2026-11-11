import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "servo/ports/geckolib/glue.rs"
NEW = "testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    lean = args.lean.resolve()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    candidates = json.loads((HERE / "CANDIDATE.json").read_text())
    for name, digest in sources["files"].items():
        data = (HERE / "source" / name).read_bytes()
        assert sha(data) == digest
        assert subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                        sources["revision"] + ":" + name], cwd=ROOT) == data
    for name, digest in candidates.items():
        assert sha((HERE / "candidate" / name).read_bytes()) == digest
    commands = {}

    def run(label, command, work, allowed_failure=False):
        p = subprocess.run([str(x) for x in command], cwd=work, capture_output=True,
                           env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE="1"))
        output = p.stdout + p.stderr
        (out / (label + ".log")).write_bytes(output)
        commands[label] = {"exit": p.returncode, "sha256": sha(output)}
        if not allowed_failure:
            assert p.returncode == 0 and not re.search(rb"\b(?:warning|error):", output), output.decode()
        return p.returncode, output.decode()

    with tempfile.TemporaryDirectory(prefix="range-order-check-") as directory:
        work = Path(directory)
        _, version = run("version", [lean, "--version"], work)
        assert "version 4.35.0-rc4," in version and "commit c29b6dda4f7c20e3eeaa717c4e565663c5cfa364" in version
        for name in sources["files"]:
            path = work / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / "source" / name, path)
        patch = HERE / "range-order.patch"
        run("apply-check", ["git", "apply", "--check", patch], work)
        run("apply", ["git", "apply", patch], work)
        for name, digest in candidates.items():
            assert sha((work / name).read_bytes()) == digest
        run("reverse-check", ["git", "apply", "--reverse", "--check", patch], work)
        run("reverse", ["git", "apply", "--reverse", patch], work)
        for name, digest in sources["files"].items():
            assert sha((work / name).read_bytes()) == digest
        assert not (work / NEW).exists()
        slots = (HERE / "Slots.lean").read_text()
        assert not re.search(r"\b(?:sorry|axiom|native_decide|unsafe)\b", slots)
        (work / "Slots.lean").write_text(slots)
        run("slots", [lean, "-o", "Slots.olean", "Slots.lean"], work)
        names = re.findall(r"(?m)^theorem (\w+)", slots)
        assert len(names) == 14
        (work / "Audit.lean").write_text("import Slots\n" + "".join(
            "#print axioms RangeGroupSlots." + name + "\n" for name in names))
        _, output = run("audit", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            m = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            assert m, line
            axioms = set(m[3].split(", ")) if m[3] else set()
            assert axioms <= {"propext", "Quot.sound", "Classical.choice"}
            assert m[1] not in audits
            audits[m[1]] = sorted(axioms)
        assert set(audits) == {"RangeGroupSlots." + name for name in names}
        controls = {}
        for label, proposition in [
            ("reuse-without-freshness", "([3, 4].set 1 3).Nodup"),
            ("zip-without-alignment", "([0, 1, 2].zip ([4, 5] : List Nat)).length = 3")]:
            (work / "FalseClaim.lean").write_text("import Slots\nexample : " + proposition + " := by decide\n")
            code, output = run(label, [lean, "FalseClaim.lean"], work, allowed_failure=True)
            assert code != 0 and output.count("error:") == 1 and "proved that the proposition" in output and "is false" in output, output
            assert not re.search(r"unknownIdentifier|unknown identifier|stuck|failed to synthesize", output)
            controls[label] = {"false_proposition": proposition, "rejected": True}
        for name in candidates:
            if not name.endswith(".html"):
                continue
            html = (HERE / "candidate" / name).read_text()
            scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.S)
            inline = "\n".join(scripts)
            (work / "test.js").write_text(inline)
            run("syntax-" + Path(name).stem, ["node", "--check", work / "test.js"], work)
        run("rustfmt", ["rustfmt", "--check", "--config-path", ROOT / "servo/rustfmt.toml",
                        HERE / "candidate" / NATIVE], work)
    total = 0
    for length in range(8):
        for word in itertools.product(range(3), repeat=length):
            frames, positions, grouped = [], [], set()
            for source_position in reversed(range(length)):
                group = word[source_position]
                found = next((i for i, frame in enumerate(frames) if frame[0] == group), None)
                if found is None:
                    frames.append((group, []))
                    positions.append(source_position)
                    slot = len(frames) - 1
                else:
                    slot = found
                    grouped.add(slot)
                    positions[slot] = source_position
                frames[slot][1].append((source_position % 2, source_position))
                assert len(frames) == len(positions) and len(set(positions)) == len(positions)
            for slot in grouped:
                seen, kept = set(), []
                for prop, value in frames[slot][1]:
                    if prop not in seen:
                        seen.add(prop)
                        kept.append((prop, value))
                frames[slot][1][:] = kept
            ordered = [frame for _, frame in sorted(zip(positions, frames))]
            expected_groups = list(dict.fromkeys(word))
            assert [frame[0] for frame in ordered] == expected_groups
            for group, values in ordered:
                expected_values = {i % 2: i for i, key in enumerate(word) if key == group}
                assert dict(values) == expected_values and len(values) == len(expected_values)
            total += 1
    report = {"status": "pass", "source_revision": sources["revision"],
              "patch_sha256": sha((HERE / "range-order.patch").read_bytes()),
              "candidate_sha256": candidates, "slots_sha256": sha((HERE / "Slots.lean").read_bytes()),
              "axiom_audits": audits, "false_claim_controls": controls,
              "finite_model_cases": total, "commands": commands,
              "temporary_outputs_removed": True, "native_build": False,
              "browser_execution": False, "wpt_lint": False, "native_refinement_proved": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits, {len(controls)} false-claim controls, {total} finite model cases")


if __name__ == "__main__":
    main()
