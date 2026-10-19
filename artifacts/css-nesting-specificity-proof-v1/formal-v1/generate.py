from pathlib import Path
import json

BASE = Path(__file__).resolve().parent

def literal(spec=(0, 0, 0), flags="{}"):
    return f"(.leaf ⟨⟨{spec[0]}, {spec[1]}, {spec[2]}⟩, {flags}⟩)"

def fold(kind, children):
    result = literal()
    for child in children:
        result = f"(.{kind} {result} {child})"
    return result

def component(c):
    k = c["kind"]
    if k in ("id", "class", "type"):
        v = [0, 0, 0]
        v[("id", "class", "type").index(k)] = c["count"]
        return literal(v)
    if k == "parent": return fold("sum", [".parent"] * c["count"])
    if k == "scope": return literal((0, c["count"], 0), "{ scope := true }")
    result = fold("max", [selector(s) for s in c["args"]])
    if k == "where": result = f"(.whereZero {result})"
    if k in ("host", "nth"):
        result = f'(.sum {literal((0, 1, 0), "{ host := true }" if k == "host" else "{}")} {result})'
    if k == "slotted": result = f'(.sum {literal((0, 0, 1), "{ slotted := true }")} {result})'
    return result

def selector(s): return f'(.header {fold("sum", [component(c) for c in s])})'

def generate(cases):
    lines = ["namespace Nesting", "def flagBits (f : Flags) : Nat := (if f.pseudo then 1 else 0) + (if f.slotted then 2 else 0) + (if f.part then 4 else 0) + (if f.parent then 8 else 0) + (if f.host then 16 else 0) + (if f.scope then 32 else 0)"]
    for row in cases:
        parent = fold("max", [selector(s) for s in row["parent_ast"]])
        child = selector(row["child_ast"])
        lines.append(f'#eval let p := eval empty {parent}; let v := eval empty (substitute p {child}); (pack v.spec, flagBits v.flags)')
    return "\n".join(lines + ["end Nesting", ""])

if __name__ == "__main__":
    model = (BASE / "Specificity.lean").read_text()
    cases = json.loads((BASE.parent / "cases.json").read_text())
    (BASE / "Cases.lean").write_text(model + generate(cases))
