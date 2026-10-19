import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ZERO = (0, 0, 0)

def add(*values):
    return tuple(sum(v[i] for v in values) for i in range(3))

def clamp(value):
    return tuple(min(1023, x) for x in value)

def packed(value):
    a, b, c = value
    return (a << 20) | (b << 10) | c

def atom(kind, count=1):
    return {"kind": kind, "count": count}

def fun(kind, *args):
    return {"kind": kind, "args": args}

def render(selector):
    out = []
    for c in selector:
        k = c["kind"]
        if k in ("id", "class", "type", "parent", "scope"):
            token = {"id": "#p", "class": ".x", "type": "x", "parent": "&", "scope": ":scope"}[k]
            out.append((" ".join([token] * c["count"])) if k == "type" else token * c["count"])
        elif k in ("is", "not", "where", "has", "nth", "host", "slotted"):
            args = ", ".join(render(s) for s in c["args"])
            if k == "has": args = ", ".join("> " + render(s) for s in c["args"])
            name = {"nth": ":nth-child(1 of ", "slotted": "::slotted("}.get(k, ":" + k + "(")
            out.append(name + args + ")")
        else:
            raise ValueError(k)
    return "".join(out)

def evaluate(selector, parent=None):
    total = ZERO
    flags = 0
    for c in selector:
        k = c["kind"]
        if k in ("id", "class", "type"):
            values = {"id": (c["count"], 0, 0), "class": (0, c["count"], 0), "type": (0, 0, c["count"])}
            value, bits = values[k], 0
        elif k == "scope":
            value, bits = (0, c["count"], 0), 32
        elif k == "parent":
            if parent is None: value, bits = ZERO, 8
            else:
                children = [evaluate(s) for s in parent]
                value = tuple(max(x[0] for x in children)[i] * c["count"] for i in range(3))
                bits = 0
                for _, f in children: bits |= f & ~7
        else:
            children = [evaluate(s, parent) for s in c["args"]]
            value = max(x[0] for x in children)
            bits = 0
            for _, f in children: bits |= f
            if k == "where": value = ZERO
            if k in ("host", "nth"): value = add(value, (0, 1, 0))
            if k == "host": bits |= 16
            if k == "slotted":
                value = add(value, (0, 0, 1))
                bits |= 2
        total = add(total, value)
        flags |= bits
    return clamp(total), flags

def cases():
    P = [atom("parent")]
    C = [atom("class")]
    T = [atom("type")]
    I = [atom("id")]
    parents = [[I], [C], [T], [I, C], [C, I], [[atom("id"), atom("class")]], [[atom("scope")]]]
    children = [("direct", P), ("repeat", [atom("parent", 3)]),
                ("is-class", [fun("is", P, C)]), ("is-type", [fun("is", P, T)]),
                ("not", [fun("not", P, C)]), ("has", [fun("has", P, C)]),
                ("nth", [fun("nth", P, C)]), ("where", [fun("where", P, I)]),
                ("host", [fun("host", [fun("is", P, C)])]),
                ("slotted", [fun("slotted", [fun("is", P, C)])]),
                ("residual", C + [fun("is", P, C)]),
                ("two-functions", [fun("is", P, C), fun("not", P, T)]),
                ("deep", [fun("is", [fun("not", P, C)], T)]),
                ("where-offset", [fun("nth", [fun("where", P, I)], C)]),
                ("unchanged-max", [fun("is", P, [atom("id", 3)])]),
                ("no-parent", C)]
    result = []
    def put(name, parent, child):
        value, flags = evaluate(child, parent)
        result.append({"name": name, "parent_ast": parent, "child_ast": child,
                       "parent": ", ".join(render(s) for s in parent), "child": render(child),
                       "specificity": packed(value), "triple": value, "flags": flags,
                       "domain": "valid-parent"})
    for pi, parent in enumerate(parents):
        for name, child in children: put(f"p{pi}-{name}", parent, child)
    for n in (1022, 1023, 1024):
        for kind in ("id", "class", "type"):
            parent = [[atom(kind, n)]]
            put(f"saturation-{kind}-{n}", parent, [fun("is", P, C)])
            put(f"saturation-sum-{kind}-{n}", parent, [atom("parent", 2)])
        put(f"residual-saturated-{n}", [I], [atom("class", n), fun("is", P, [atom("class", n)])])
    return result

def main():
    values = cases()
    (BASE / "cases.json").write_text(json.dumps(values, indent=2) + "\n")
    (BASE / "cases.tsv").write_text("".join(f'{v["name"]}\t{v["parent"]}\t{v["child"]}\n' for v in values))

if __name__ == "__main__": main()
