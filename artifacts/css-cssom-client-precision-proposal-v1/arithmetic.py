import json
import math
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent


def f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def truncate(value, divisor):
    return value // divisor if value >= 0 else -((-value) // divisor)


def exact_client(value):
    return truncate(value + (30 if value >= 0 else -29), 60)


rows = []
for base in [16, 16777200]:
    for extra in [0, 17]:
        native = 60 * (base + extra)
        quotient = f32(f32(native) / 60)
        rows.append({"base": base, "extra": extra, "conditional_native_input": native,
                     "float_native": f32(native), "float_css": quotient,
                     "client_floor": math.floor(quotient + 0.5),
                     "old_scroll_round": int(f32(quotient + f32(0.5))),
                     "exact_client": exact_client(native),
                     "below_named_nscoord_max": native < 1073741823,
                     "endpoint_at_40px_below_named_nscoord_max": native + 2400 < 1073741823})
assert [row["client_floor"] for row in rows] == [16, 33, 16777200, 16777218]
assert [row["exact_client"] for row in rows] == [16, 33, 16777200, 16777217]
samples = set(range(-120, 121))
samples.update(range(-2147483648, -2147483648 + 120))
samples.update(range(2147483647 - 120, 2147483647 + 1))
for value in samples:
    assert exact_client(value) == (value + 30) // 60
    assert -2147483648 <= exact_client(value) <= 2147483647
assert exact_client(-30) == 0 and exact_client(-31) == -1
result = {"kind": "source-shaped arithmetic, no native/browser execution",
          "binary32_assumption": "round-to-nearest-even conversion and division",
          "rows": rows, "integer_formula_checked_samples": len(samples),
          "negative_half": {"input": -30, "client": exact_client(-30), "offset": -1}}
(HERE / "ARITHMETIC.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
