import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check():
    for name, digest in json.loads((HERE / "INPUTS.json").read_text()).items():
        assert sha(ROOT / name) == digest, name
    review = ROOT / "artifacts/css-flex-wide-caller-proof-root-review-20261111-v1"
    assert sha(review / "FILES.json") == "3b7eb6a4022a73670ffa9daf71c02d56bc3e5f3ddfef057ad5db231c88941271"
    inventory = json.loads((review / "FILES.json").read_text())
    for name, digest in inventory.items():
        assert sha(review / name) == digest, name
    current = json.loads((HERE / "CURRENT-SOURCE.json").read_text())
    for name, digest in current.items():
        assert sha(ROOT / name) == digest, name
        assert sha(HERE / "origins" / Path(name).name) == digest, name
    old = (ROOT / "artifacts/css-flex-wide-caller-design-20261111-v1/origins/nsFlexContainerFrame.cpp").read_text()
    assert old.count("float GetWeight(bool aIsUsingFlexGrow)") == 1
    assert old.count("return mFlexShrink * mFlexBaseSize;") == 1
    expected = old.replace("float GetWeight(bool aIsUsingFlexGrow)", "double GetWeight(bool aIsUsingFlexGrow)").replace("return mFlexShrink * mFlexBaseSize;", "return double(mFlexShrink) * mFlexBaseSize;")
    actual = (HERE / "origins/nsFlexContainerFrame.cpp").read_text()
    assert actual == expected
    assert actual.count("line.ResolveFlexibleLengths(flr.mContentBoxMainSize, lineInfo);") == 1
    return {"status": "PASS", "scope": "byte authentication and exact two-line source-version delta; no native refinement proof", "review_files": len(inventory), "native_sources": len(current)}

if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
