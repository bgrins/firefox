import json
import re
from pathlib import Path

SOURCES = [
    "0", "-0", "+12x", "00123!", ".5;", "-.5", "1.20", "1.", "1e2x", "1E-2!",
    "1e+", "1.ee2", "1ee2", "1e-0", "123456789012345678901234567890.125e-7!",
    "1e999999999999999999999999999999!", "9" * 128 + "e-140!", "", "e2", "+.", "١2",
]


def rows(changed=False):
    exponent = r"[eE]*([+-]?)([0-9]+)" if changed else r"[eE]([+-]?)([0-9]+)"
    result = []
    for source in SOURCES:
        match = re.match(r"([+-]?)([0-9]*)(?:\.([0-9]+))?", source)
        sign, integer, fraction = match.groups()
        rest = source[match.end():]
        exp = re.match(exponent, rest)
        scale = -(len(fraction) if fraction is not None else 0)
        if exp is not None:
            scale += int(exp.group(1) + exp.group(2))
            rest = rest[exp.end():]
        significand = int(integer + (fraction or "") or "0")
        if sign == "-":
            significand = -significand
        for error in (False, True):
            result.append({"source": source, "error_before": error, "rest": rest,
                "error_after": error, "matched": True, "significand": str(significand),
                "scale": str(scale), "type": "number" if fraction is not None or exp is not None else "integer",
                "sign": sign or None})
    return result


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    for changed, name in ((False, "expected.json"), (True, "changed-expected.json")):
        (base / name).write_text(json.dumps(rows(changed), indent=2, ensure_ascii=False) + "\n")
