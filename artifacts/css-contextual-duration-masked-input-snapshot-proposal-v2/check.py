import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name, record in json.loads((HERE / "REFERENCES.json").read_text()).items():
        path = ROOT / name
        assert sha(path) == record["sha256"] and path.stat().st_size == record["bytes"]
    roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
    assert len(roles) == 8
    spec = importlib.util.spec_from_file_location("snapshot_generate", HERE / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.generate()
    assert set(generated) == set(roles)
    for name, record in roles.items():
        assert sha(ROOT / record["base_capture"]) == record["base_sha256"]
        assert sha(ROOT / record["candidate_capture"]) == record["candidate_sha256"]
        assert (ROOT / record["candidate_capture"]).read_text() == generated[name]
    for name, record in json.loads((HERE / "FROZEN-BASES.json").read_text()).items():
        assert sha(ROOT / record["path"]) == record["sha256"] == sha(HERE / "base" / name)
    for name, record in json.loads((HERE / "CAPTURE.json").read_text())["files"].items():
        assert sha(ROOT / record["capture"]) == record["sha256"]
    with tempfile.TemporaryDirectory(prefix="masked-snapshot-patch-") as scratch:
        target = Path(scratch)
        for name in roles:
            dst = target / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / "base" / name, dst)
        patch = (HERE / "native.patch").read_bytes()
        for reverse, expected in [(False, "candidate_sha256"), (True, "base_sha256")]:
            command = ["patch", "--batch", "-p1"] + (["-R"] if reverse else [])
            result = subprocess.run(command, cwd=target, input=patch, capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name, record in roles.items():
                assert sha(target / name) == record[expected]
    previous = ROOT / "artifacts/css-contextual-duration-masked-input-snapshot-proposal-v1"
    previous_roles = json.loads((previous / "SOURCE-ROLES.json").read_text())
    for name, record in previous_roles.items():
        assert roles[name]["base_sha256"] == record["base_sha256"]
        assert roles[name]["candidate_sha256"] == record["candidate_sha256"]
    receipt = json.loads((ROOT / "artifacts/css-masked-snapshot-forward-declaration-equivalence-v1.json").read_text())
    header = roles["layout/style/GeckoBindings.h"]
    assert receipt["path"] == "layout/style/GeckoBindings.h"
    assert receipt["sha256"] == receipt["original_build_pin"] == header["base_sha256"]
    assert receipt["bytes"] == (ROOT / header["base_capture"]).stat().st_size
    assert receipt["committed_versions"] == {revision: header["base_sha256"] for revision in (
        "ecfe313d582a335c04d80bfd360fd3a591defdb7", "20ab7e723b663c0f78c8490e60a6fccc5e65cc99")}
    assert not receipt["native_mutated"] and not receipt["git_mutated"]
    def widths(bodies):
        assert "enum class UpdateAnimationsTasks : uint16_t;" in bodies["layout/style/GeckoBindings.h"]
        assert "enum class UpdateAnimationsTasks : uint16_t {" in bodies["layout/style/ServoTypes.h"]
        assert "pub struct UpdateAnimationsTasks: u16 {" in bodies["servo/components/style/context.rs"]
    widths(generated)
    wrong = dict(generated)
    wrong["layout/style/GeckoBindings.h"] = wrong["layout/style/GeckoBindings.h"].replace("UpdateAnimationsTasks : uint16_t;", "UpdateAnimationsTasks : uint8_t;")
    try:
        widths(wrong)
    except AssertionError:
        pass
    else:
        raise AssertionError("old forward declaration width admitted")
    manager = generated["layout/style/nsAnimationManager.cpp"]
    assert manager.index("mLastAnimationDurationInput = std::move") < manager.index("// Cancel removed animations")
    assert "ServoCSSAnimationBuilder builder(aComputedStyle)" in manager
    assert "*aComputedStyle->StyleUIReset(), builder" in manager
    bindings = generated["layout/style/GeckoBindings.cpp"]
    assert "const_cast<Element*>(aElement), aComputedData" in bindings
    assert "const bool verifyOnly = !(aTasks & UpdateAnimationsTasks::CSSAnimations)" in bindings
    assert "pub struct UpdateAnimationsTasks: u16" in generated["servo/components/style/context.rs"]
    assert "enum class UpdateAnimationsTasks : uint16_t" in generated["layout/style/ServoTypes.h"]
    print(json.dumps({"eight_source_generation": True, "forward_reverse_exact": True,
                      "owned_scratch_removed": True, "native_compile": False,
                      "browser_execution": False}, sort_keys=True))


if __name__ == "__main__":
    main()
