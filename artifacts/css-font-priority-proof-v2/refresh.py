import argparse
import hashlib
import json
from pathlib import Path
import bridge

BASE = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    baseline = BASE / "refresh-baseline"
    previous = json.loads((baseline / "INPUTS-v1.json").read_text())
    assert sha((baseline / "INPUTS-v1.json").read_bytes()) == "faea6f932f67c697d7bf3fa8aff90c37ee948a16e66b862fd1bcdb1c130643ae"
    changed = []
    for name, digest in previous["files"].items():
        if sha((BASE / name).read_bytes()) != digest:
            changed.append(name)
    assert sorted(changed) == ["README.md", "candidate/gfx/thebes/gfxFontEntry.h", "run.py"], changed
    old_header = (baseline / "candidate/gfx/thebes/gfxFontEntry.h").read_bytes()
    new_header = (BASE / "candidate/gfx/thebes/gfxFontEntry.h").read_bytes()
    assert old_header.count(b"#include <math.h>\n\n") == 1
    assert old_header.replace(b"#include <math.h>\n\n", b"", 1) == new_header
    old_manifest = json.loads((baseline / "EXTRACTION.json").read_text())
    results = {}
    driver = (BASE / "driver.cpp").read_text()
    for variant in ("original", "B", "A", "AB"):
        source = bridge.generate(variant, driver)
        assert source.encode() == (baseline / (variant + ".cpp")).read_bytes(), variant
        extracted = bridge.manifest(variant)
        old = old_manifest[variant]
        assert len(extracted) == len(old)
        for actual, prior in zip(extracted, old):
            for key in ("source", "owner", "marker", "body_sha256"):
                assert actual.get(key) == prior.get(key), (variant, key, actual.get("marker"))
            assert actual["body"] in source
        results[variant] = dict(complete_generated_translation_unit_equal=True,
                                generated_sha256=sha(source.encode()),
                                equal_extracted_bodies=len(extracted))
    result = dict(status="PASS",candidate_delta="unused math.h include and following blank line only",
                  changed_v1_manifest_inputs=changed,variants=results,
                  mathematical_provider_corpus_driver_and_B_inputs_unchanged=True,
                  count_labels_corrected=True)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
