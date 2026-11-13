from pathlib import Path
import hashlib
import importlib.util
import json

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("audit_parser", base / "audit_parser.py")
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
plan = json.loads((base / "AUDIT-PLAN.json").read_text())
inherited = json.loads((base / "INHERITED-AUDIT.json").read_text())
contract = json.loads((base / "CONTRACT.json").read_text())
old = [[name, inherited[name]] for name in plan["inherited_exact_names"]]
assert len(old) == 50 and len(plan["new_theorems"]) == 32
assert list(inherited) == plan["inherited_exact_names"]
assert plan["names"] == list(inherited) + plan["new_theorems"]
assert contract["final_exact_new_axiom_map"] is None
assert contract["final_proof_types_sha256"] is None
retained = (base / "retained-definition-audit.log").read_bytes()
parser.validate(retained, old)
types = (base / "retained-definition-types.log").read_bytes()
parser.validate_types(types, contract["protected_types_sha256"])
warning = (base / "retained-definition-controls.log").read_bytes()
parser.validate_warning(warning, warning)
expected = old + [[name, []] for name in plan["new_theorems"]]


def render(rows):
    return ("\n".join("'" + name + "' " +
        ("depends on axioms: [" + ", ".join(axes) + "]" if axes else
         "does not depend on any axioms") for name, axes in rows) + "\n").encode("ascii")


raw = render(expected)
parser.validate(raw, expected)
refusals = []


def refuse(name, callback):
    try:
        callback()
    except ValueError as error:
        refusals.append({"id": name, "result": "REFUSED", "reason": str(error)})
    else:
        raise AssertionError("Control unexpectedly accepted: " + name)


def audit(name, value):
    refuse(name, lambda: parser.validate(value, expected))


audit("omitted-inherited", render(expected[:4] + expected[5:]))
audit("omitted-new", render(expected[:-1]))
audit("extra-unknown", raw + render([["Unknown.declaration", []]]))
audit("reordered-inherited", render([expected[1], expected[0]] + expected[2:]))
audit("reordered-new", render(expected[:50] + [expected[51], expected[50]] + expected[52:]))
audit("duplicate-declaration", raw + render([expected[-1]]))
for name, axes in [("forbidden-sorry", ["sorryAx"]), ("forbidden-native-decide", ["Lean.ofReduceBool"]),
                   ("forbidden-custom", ["Unexpected.assumption"]),
                   ("changed-new-standard", ["Classical.choice"]),
                   ("duplicate-axiom", ["propext", "propext"])]:
    audit(name, render(expected[:50] + [[expected[50][0], axes]] + expected[51:]))
audit("missing-inherited-axiom", render(expected[:5] + [[expected[5][0], []]] + expected[6:]))
audit("reordered-inherited-axioms", render(expected[:5] + [[expected[5][0], list(reversed(expected[5][1]))]] + expected[6:]))
audit("extra-inherited-axiom", render(expected[:5] + [[expected[5][0], expected[5][1] + ["Classical.choice"]]] + expected[6:]))
audit("warning-line", b"warning: unexpected\n" + raw)
audit("blank-line", raw + b"\n")
audit("garbage-suffix", raw + b"garbage\n")
audit("missing-final-newline", raw[:-1])
audit("crlf", raw.replace(b"\n", b"\r\n"))
audit("nonascii", raw + "é\n".encode())
audit("extra-space", b" " + raw)
audit("malformed-axiom-list", raw.replace(b"[propext, Quot.sound]", b"[propext,Quot.sound]", 1))
refuse("changed-types", lambda: parser.validate_types(types + b"\n", contract["protected_types_sha256"]))
refuse("missing-warning", lambda: parser.validate_warning(b"", warning))
refuse("extra-warning", lambda: parser.validate_warning(warning + b"warning: unexpected\n", warning))
refuse("changed-warning-path", lambda: parser.validate_warning(warning.replace(b"Controls.lean", b"Other.lean"), warning))
refuse("changed-warning-binder", lambda: parser.validate_warning(warning.replace(b"`b`", b"`d`", 1), warning))
print(json.dumps({"status": "PASS", "scope": "Pure-Python retained/synthetic transcript parser only",
    "retained_definition_records": 50, "synthetic_proof_records": 82,
    "synthetic_new_axioms": "32 empty dummy lists; no theorem dependency claim",
    "refusal_count": len(refusals), "refusals": refusals,
    "new_lean_proofs_checked": 0, "native_cells_checked": 0}, indent=2))
