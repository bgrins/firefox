import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root, policy, source):
    binding = policy["baseline_binding"]
    assert binding is not None
    directory = root / policy["baseline_capsule"]["directory"]
    spec = importlib.util.spec_from_file_location("expanded_original_saved_admission", directory / "check.py")
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    original.check_binding(source)
    assert policy["head"] == source["head"]
    assert policy["controls"] == source["controls"]
    assert policy["prepared_application_metadata"] == {k:v for k,v in source["prepared_application_metadata"].items() if k not in ("build_revision", "harness_revision", "source_role")}
    assert policy["source_context_pins"] == source["source_role_pins"]
    assert policy["accepted_current_payloads"] == source["accepted_current_payloads"]
    assert binding["directory"] == source["output"]
    runtime = root / binding["directory"]
    assert sha(runtime / "FILES.json") == binding["manifest_sha256"]
    for name, record in read(runtime / "FILES.json").items():
        path = runtime / name
        assert not path.is_symlink() and path.is_file()
        assert sha(path) == (record if isinstance(record, str) else record["sha256"]), name
        if isinstance(record, dict):
            assert path.stat().st_size == record["bytes"]
    terminal = read(runtime / binding["terminal_path"])
    assert terminal == binding["terminal"]
    assert terminal["owner_sha256"] == policy["baseline_capsule"]["sha256"]
    assert terminal["result_sha256"] == binding["result_sha256"] == sha(runtime / "RESULT.json")
    assert terminal["exit"] == 0 and terminal["native_acceptance"] is False
    assert terminal["callbacks_passed"] + terminal["callbacks_failed"] == 120
    assert terminal["page_endings_ok"] == 16
    assert all(terminal[k] for k in ("raw_replay_verified", "pre_post_equality_verified", "current_source_binary_control_pins_verified", "owned_process_cleanup_verified"))
    assert read(runtime / "PRE.json") == read(runtime / "POST.json")
