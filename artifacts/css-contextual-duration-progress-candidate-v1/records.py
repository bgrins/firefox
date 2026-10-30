import hashlib
import importlib.util
import json
import os
import stat


def load(path):
    spec = importlib.util.spec_from_file_location("progress_schema_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect(root, directory, binding, policy, assessment):
    expected = policy["record_kinds"]
    rows = {(row["test"], row["subtest"]): row for row in assessment["rows"]}
    errors, missing, records = [], [], {}
    info = directory.lstat()
    assert stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == binding["identity"]
    assert stat.S_IMODE(info.st_mode) == 0o700 and info.st_uid == os.getuid()
    assert str(directory) == binding["directory"]
    present = {path.name for path in directory.iterdir()}
    if present - set(expected):
        errors.append("Unknown record names: " + repr(sorted(present - set(expected))))
    for filename, rule in expected.items():
        row = rows[(rule["page"], rule["subtest"])]
        if filename not in present:
            missing.append({"file": filename, "test": rule["page"], "subtest": rule["subtest"], "status": row["status"], "reason": "No envelope retained; acquisition or collection may have failed before POST"})
            if row["status"] == "PASS":
                errors.append("PASS callback lacks record: " + filename)
            continue
        path = directory / filename
        try:
            info = path.lstat()
            assert stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
            assert info.st_uid == os.getuid() and info.st_nlink == 1 and info.st_size <= 65536
            body = path.read_bytes()
            records[filename] = {"sha256": hashlib.sha256(body).hexdigest(), "identity": [info.st_dev, info.st_ino], "mode": stat.S_IMODE(info.st_mode), "bytes": len(body), "callback_status": row["status"], "schema_valid": False}
            schema = load(root / rule["schema"])
            record = json.loads(body, parse_constant=schema.reject_constant)
            assert set(record) == {"run_id", "kind", "observation"} and record["run_id"] == binding["run_id"]
            assert schema.validate({key: value for key, value in record.items() if key != "run_id"}) == rule["kind"]
            records[filename]["schema_valid"] = True
        except (AssertionError, ValueError, KeyError, TypeError, OSError) as error:
            errors.append(filename + ": " + repr(error))
    return {"run_id": binding["run_id"], "records": records, "missing": missing, "errors": errors,
            "complete": not missing and not errors, "expected_records": len(expected),
            "numeric_or_convergence_oracle": False, "callback_outcomes_are_separate": True}
