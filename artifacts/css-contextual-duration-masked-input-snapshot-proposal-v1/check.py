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
    assert len(roles) == 7
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
    manager = generated["layout/style/nsAnimationManager.cpp"]
    assert manager.index("mLastAnimationDurationInput = std::move") < manager.index("// Cancel removed animations")
    assert "ServoCSSAnimationBuilder builder(aComputedStyle)" in manager
    assert "*aComputedStyle->StyleUIReset(), builder" in manager
    bindings = generated["layout/style/GeckoBindings.cpp"]
    assert "const_cast<Element*>(aElement), aComputedData" in bindings
    assert "const bool verifyOnly = !(aTasks & UpdateAnimationsTasks::CSSAnimations)" in bindings
    assert "pub struct UpdateAnimationsTasks: u16" in generated["servo/components/style/context.rs"]
    assert "enum class UpdateAnimationsTasks : uint16_t" in generated["layout/style/ServoTypes.h"]
    print(json.dumps({"seven_source_generation": True, "forward_reverse_exact": True,
                      "owned_scratch_removed": True, "native_compile": False,
                      "browser_execution": False}, sort_keys=True))


if __name__ == "__main__":
    main()
