import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFINITIONS = {
    "hexExpr": ("scalar", "bool"),
    "whitespaceExpr": ("scalar", "bool"),
    "magnitudeExpr": ("chars", "nat"),
    "decodeExpr": ("nat", "scalar"),
}


def node(op, *args):
    return {"op": op, "args": list(args)}


def expression_definitions(parameters):
    deps, cfg = parameters["dependencies"], parameters["program"]
    c, n = node("var", 0), node("var", 0)
    nat = lambda value: node("nat", value)
    scalar = lambda value: node("scalar", value)
    def within(bounds):
        return node("and", node("leChar", scalar(bounds[0]), c), node("leChar", c, scalar(bounds[1])))
    digit, upper, lower = [deps[key] for key in ["digit_range", "upper_hex_range", "lower_hex_range"]]
    hex_expr = node("or", node("or", within(digit), within(upper)), within(lower))
    whites = [node("eqChar", c, scalar(value)) for value in deps["whitespace"]]
    whitespace = node("or", node("or", whites[0], whites[1]), whites[2])
    digit_value = node("ite", node("leChar", c, scalar(digit[1])), node("sub", node("code", c), nat(digit[0])),
        node("ite", node("leChar", c, scalar(upper[1])), node("sub", node("code", c), nat(upper[0] - 10)), node("sub", node("code", c), nat(lower[0] - 10))))
    magnitude = node("foldNat", node("var", 0), nat(0), node("add", node("mul", node("var", 1), nat(cfg["base"])), digit_value))
    invalid = node("or", node("or", node("eqNat", n, nat(0)), node("and", node("leNat", nat(deps["surrogate_range"][0]), n), node("leNat", n, nat(deps["surrogate_range"][1])))), node("ltNat", nat(deps["maximum"]), n))
    decoded = node("ite", invalid, scalar(cfg["invalid_replacement"]), node("scalarOf", n))
    return {"hexExpr": hex_expr, "whitespaceExpr": whitespace, "magnitudeExpr": magnitude, "decodeExpr": decoded}


def build(parameters):
    cfg = parameters["program"]
    if not all(cfg[key] for key in ["read_first", "zero_is_invalid", "surrogate_is_invalid", "maximum_is_inclusive", "eof_error"]):
        raise ValueError("Unsupported reviewed escape contract")
    program = node("read",
        node("raiseError", node("ret", node("scalar", cfg["eof_replacement"]))),
        node("branch", node("use", "hexExpr"),
            node("scan", cfg["hex_additional_limit"], node("use", "hexExpr"),
                node("scan", cfg["terminator_limit"], node("use", "whitespaceExpr"),
                    node("letE", node("cons", node("var", 2), node("var", 1)),
                        node("letE", node("use", "magnitudeExpr"), node("ret", node("use", "decodeExpr")))))),
            node("ret", node("var", 0))))
    return {
        "schema": 1,
        "definitions": expression_definitions(parameters),
        "program": program,
        "source_map": {
            "algorithm": {"anchor": parameters["anchor"], "source_bytes": parameters["source_bytes"]},
            "body": {"source_bytes": parameters["body_source_bytes"], "operative_text": parameters["operative_text"]},
            "definitions": deps_map(parameters),
            "roles": {
                "read": "Initial next-input consumption and EOF/literal dispatch",
                "first scan": "Maximal bounded additional hex consumption",
                "second scan": "Conditional single whitespace terminator",
                "first local": "Assemble first consumed scalar plus additional hex digits",
                "second local": "Interpret the hex digits as a hexadecimal number",
                "decodeExpr": "Zero/surrogate/maximum replacement or scalar result",
            },
        },
    }


def deps_map(parameters):
    return parameters["dependencies"]["definitions"]


def natural(value):
    if type(value) is not int or value < 0:
        raise ValueError("Expected a natural-number literal")
    return str(value)


def variable(index):
    natural(index)
    result = ".here"
    for _ in range(index):
        result = "(.there " + result + ")"
    return result


def unpack(value):
    if type(value) is not dict or set(value) != {"op", "args"} or type(value["args"]) is not list:
        raise ValueError("Expected a data-only constructor object")
    return value["op"], value["args"]


def emit_expr(value):
    op, args = unpack(value)
    arities = {"code": 1, "scalarOf": 1, "add": 2, "sub": 2, "mul": 2,
        "leNat": 2, "ltNat": 2, "eqNat": 2, "leChar": 2, "eqChar": 2,
        "and": 2, "or": 2, "ite": 3, "cons": 2, "foldNat": 3, "nil": 0, "unit": 0}
    if op in arities and len(args) == arities[op]:
        return "(." + op + (" " if args else "") + " ".join(emit_expr(a) for a in args) + ")"
    if op == "nat" and len(args) == 1:
        return "(.nat " + natural(args[0]) + ")"
    if op == "scalar" and len(args) == 1:
        natural(args[0])
        if args[0] > 0x10ffff or 0xd800 <= args[0] <= 0xdfff:
            raise ValueError("Invalid scalar literal")
        return "(.scalar (Char.ofNat " + str(args[0]) + "))"
    if op == "bool" and len(args) == 1 and type(args[0]) is bool:
        return "(.bool " + str(args[0]).lower() + ")"
    if op == "var" and len(args) == 1:
        return "(.var " + variable(args[0]) + ")"
    if op == "use" and len(args) == 1 and args[0] in DEFINITIONS:
        return args[0]
    raise ValueError("Unsupported expression constructor/arity: " + str(op))


def emit_stmt(value):
    op, args = unpack(value)
    if op == "ret" and len(args) == 1:
        return "(.ret " + emit_expr(args[0]) + ")"
    if op == "letE" and len(args) == 2:
        return "(.letE " + emit_expr(args[0]) + " " + emit_stmt(args[1]) + ")"
    if op == "read" and len(args) == 2:
        return "(.read " + emit_stmt(args[0]) + " " + emit_stmt(args[1]) + ")"
    if op == "scan" and len(args) == 3:
        return "(.scan " + natural(args[0]) + " " + emit_expr(args[1]) + " " + emit_stmt(args[2]) + ")"
    if op == "raiseError" and len(args) == 1:
        return "(.raiseError " + emit_stmt(args[0]) + ")"
    if op == "branch" and len(args) == 3:
        return "(.branch " + emit_expr(args[0]) + " " + emit_stmt(args[1]) + " " + emit_stmt(args[2]) + ")"
    raise ValueError("Unsupported statement constructor/arity: " + str(op))


def emit(ast):
    if set(ast) != {"schema", "definitions", "program", "source_map"} or ast["schema"] != 1 or set(ast["definitions"]) != set(DEFINITIONS):
        raise ValueError("Unexpected AST schema")
    lines = ["import Lowering", "", "namespace CssDerivation.FirstOrder", ""]
    for name, (head, result) in DEFINITIONS.items():
        lines.extend([f"def {name} {{Γ : List Ty}} : Expr (.{head} :: Γ) .{result} :=", "  " + emit_expr(ast["definitions"][name]), ""])
    lines.extend(["def escapeTree : Stmt [] .scalar :=", "  " + emit_stmt(ast["program"]), "", "end CssDerivation.FirstOrder", ""])
    return "\n".join(lines)


def main():
    prior = json.loads((HERE / "PRIOR.json").read_text())
    for name, expected in prior["files"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Pinned prior source changed: " + name)
    spec = importlib.util.spec_from_file_location("prior_translate", HERE / "prior/translate.py")
    translator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(translator)
    parameters = translator.extract((HERE / "prior/inputs/css-syntax-3.bs").read_text(),
        (HERE / "prior/inputs/infra.bs").read_text(), "consume-escaped-code-point")
    if parameters != json.loads((HERE / "prior/generated/algorithm.json").read_text()):
        raise ValueError("Source extraction differs from the checked prior parameters")
    ast = build(parameters)
    generated = HERE / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "escape.json").write_text(json.dumps(ast, indent=2) + "\n")
    (generated / "GeneratedFirstOrder.lean").write_text(emit(ast))
    print(json.dumps({"generated": True, "syntax": "typed first-order constructors", "source_parameters_match_prior": True}))


if __name__ == "__main__":
    main()
