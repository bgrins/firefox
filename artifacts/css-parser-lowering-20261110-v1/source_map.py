import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def extract():
    metadata = json.loads((ROOT / "SOURCE.json").read_text())
    raw = (ROOT / metadata["file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
        raise ValueError("Pinned CSS source drift")
    spans = []

    def span(start, end, meaning):
        first, last = start.encode(), end.encode()
        if raw.count(first) != 1:
            raise ValueError("Ambiguous or missing source marker")
        a = raw.index(first)
        b = raw.index(last, a + len(first))
        spans.append({"start": a, "end": b, "markup": raw[a:b].decode(),
                      "sha256": hashlib.sha256(raw[a:b]).hexdigest(),
                      "manual_mapping": meaning})

    span('<h4 id="consume-number">', '<h4 id="consume-unicode-range-token">',
         "numberTree consumes exact decimal parts; project supplies numeric value/type/sign. Caller must start a number; total off-domain behavior is not a CSS claim.")
    span('\t\t<dt><dfn export>digit</dfn>', '\t\t<dt><dfn export>hex digit</dfn>',
         "digitPredicate is the inclusive ASCII 0..9 range, connected to the independently written reference predicate by digit_meaning.")
    span('<h4 id="starts-with-a-number">', '<h4 id="starts-a-unicode-range">',
         "StartsNumber is a caller obligation; the total consumer's off-domain outputs are not spec-conformance claims.")
    return {"source_revision": metadata["revision"], "mapping_is_manual": True,
            "prose_correspondence_mechanically_proved": False, "spans": spans}


if __name__ == "__main__":
    (ROOT / "CLAUSES.json").write_text(json.dumps(extract(), indent=2) + "\n")
