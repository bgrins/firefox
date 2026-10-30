from fractions import Fraction
import json


def sample(font):
    duration = Fraction(1000 * font, 32)
    return {"input_font_px": font, "duration_ms": str(duration),
            "output_font_px": 32 if Fraction(750) >= duration else 16}


rows = [sample(16), sample(32)]
assert rows[0]["output_font_px"] == 32
assert rows[1]["output_font_px"] == 16
assert all(row["input_font_px"] != row["output_font_px"] for row in rows)
print(json.dumps({"conditional_endpoint_evaluation": rows,
                  "browser_executed": False, "normative_cycle_policy_proved": False}, indent=2))
