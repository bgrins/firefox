#!/usr/bin/env python3
"""Finite refinement checks, not a proof of native code or IEEE arithmetic."""
from itertools import product
import json

AUTO = "auto"
ERROR = "error"


def component(a, b, count):
    if a == AUTO or b == AUTO:
        return AUTO if a == b else ERROR
    return count * a + b


def old_rect(a, b, count, interpolate=False):
    result = []
    for x, y in zip(a, b):
        z = component(x, y, count)
        if z == ERROR or (not interpolate and z == AUTO):
            return ERROR
        result.append(z)
    return tuple(result)


def css(a, b, count):
    if a == AUTO or b == AUTO:
        return AUTO if a == b else ERROR
    result = tuple(component(x, y, count) for x, y in zip(a, b))
    return ERROR if ERROR in result else result


def admitted(result):
    return ERROR if isinstance(result, tuple) and AUTO in result else result


def old(a, b, count):
    if a == AUTO or b == AUTO:
        return AUTO if a == b else ERROR
    return old_rect(a, b, count)


def candidate(a, b, count):
    return admitted(css(a, b, count))


def main():
    categories = 0
    for results in product((ERROR, AUTO, 7), repeat=4):
        old_result = next((ERROR for x in results if x in (ERROR, AUTO)), results)
        new_result = admitted(ERROR if ERROR in results else results)
        assert old_result == new_result
        categories += 1

    values = [AUTO] + list(product((AUTO, 0, 5), repeat=4))
    cases = 0
    for count in (0, 1, 2, (1 << 64) - 1):
        for a, b in product(values, repeat=2):
            assert old(a, b, count) == candidate(a, b, count)
            cases += 1

    numeric_a, numeric_b = (10, 50, 50, 10), (20, 60, 70, 30)
    mixed = (AUTO, 50, 50, 10)
    controls = {}
    for count in (0, 1, 2):
        expected = tuple(count * a + b for a, b in zip(numeric_a, numeric_b))
        assert candidate(numeric_a, numeric_b, count) == expected
        controls[f"numeric-count-{count}"] = list(expected)
        assert candidate(AUTO, AUTO, count) == AUTO
        controls[f"outer-auto-count-{count}"] = AUTO
        assert candidate(mixed, mixed, count) == ERROR
        controls[f"smil-mixed-count-{count}"] = ERROR
        assert css(mixed, mixed, count) == (AUTO, (count+1)*50, (count+1)*50, (count+1)*10)
        controls[f"css-mixed-count-{count}"] = list(css(mixed, mixed, count))
        assert css(mixed, numeric_a, count) == ERROR
        assert candidate(AUTO, mixed, count) == ERROR
    assert old_rect(mixed, mixed, 0, interpolate=True) == mixed
    controls["equal-auto-interpolation-tag-preserved"] = True
    assert css(mixed, mixed, 1) == (AUTO, 100, 100, 20)
    controls["css-add"] = list(css(mixed, mixed, 1))

    mutants = {
        "omit-smil-guard": lambda a, b, n: css(a, b, n),
        "reject-outer-auto": lambda a, b, n: ERROR if css(a, b, n) == AUTO else candidate(a, b, n),
        "count-zero-shortcut": lambda a, b, n: b if n == 0 else candidate(a, b, n),
        "reject-all-clip": lambda a, b, n: ERROR,
    }
    rejected = {}
    for name, mutation in mutants.items():
        witness = next(((a, b, n) for n in (0, 1, 2) for a, b in product(values, repeat=2)
                        if mutation(a, b, n) != old(a, b, n)), None)
        assert witness is not None, name
        rejected[name] = witness
    return {"status": "PASS", "abstract_result_category_cases": categories,
            "tagged_integer_cases": cases, "controls": controls, "rejected_mutants": rejected,
            "scope": "Finite model, exact integer witnesses; no IEEE/native/FFI proof. Category equivalence assumes pure total component operations."}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
