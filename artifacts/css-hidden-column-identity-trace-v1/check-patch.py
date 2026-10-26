import hashlib
import json
import re
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parent.parent
pins = json.loads((here / "SOURCE-PINS.json").read_text())
roles = {row["path"]: row for row in pins["roles"]}
lines = (here / "trace-only.patch").read_text().splitlines(keepends=True)
i = 0
results = []
while i < len(lines):
    if not lines[i].startswith("--- "):
        raise ValueError("expected file header")
    old_name = lines[i][4:].strip()
    new_name = lines[i + 1][4:].strip()[2:]
    row = roles.get(new_name)
    if old_name == "/dev/null":
        source = []
        expected = pins["header_sha256"]
    else:
        data = (root / row["source"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != row["source_sha256"]:
            raise ValueError("source drift")
        source = data.decode().splitlines(keepends=True)
        expected = row["trace_sha256"]
    i += 2
    cursor = 0
    output = []
    while i < len(lines) and lines[i].startswith("@@ "):
        match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n", lines[i])
        if not match:
            raise ValueError("unsupported hunk header")
        position = max(0, int(match[1]) - 1)
        old_count = int(match[2] or 1)
        new_count = int(match[4] or 1)
        if position < cursor:
            raise ValueError("overlapping hunk")
        output.extend(source[cursor:position])
        cursor = position
        seen_old = seen_new = 0
        i += 1
        while i < len(lines) and not lines[i].startswith(("@@ ", "--- ")):
            line = lines[i]
            if line[0] in " -":
                if cursor >= len(source) or source[cursor] != line[1:]:
                    raise ValueError("context mismatch")
                cursor += 1
                seen_old += 1
            if line[0] in " +":
                output.append(line[1:])
                seen_new += 1
            if line[0] not in " +-":
                raise ValueError("unsupported hunk line")
            i += 1
        if (seen_old, seen_new) != (old_count, new_count):
            raise ValueError("hunk count")
    output.extend(source[cursor:])
    digest = hashlib.sha256("".join(output).encode()).hexdigest()
    if digest != expected:
        raise ValueError("output mismatch")
    results.append({"path": new_name, "output_sha256": digest})
print(json.dumps({"status": "PASS_SOURCE_TEXT_ONLY", "files": results,
                  "compiled": False, "native_mutations": False}, indent=2))
