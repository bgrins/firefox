import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "css-document-library-integration-20261110-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    own = HERE / "replay"
    author = SOURCE / "verification"
    assert sha(SOURCE / "REPORT.md") == "6e533c1223b9b6b4c11861d52063f355133df7f3ee100ba10125f8270a5bd92c"
    manifest = read(SOURCE / "SOURCE-ONLY.json")
    for name, expected in manifest.items():
        assert sha(SOURCE / name) == expected
    assert read(own / "report.json")["source_sha256"] == manifest
    assert read(own / "report.json")["default_css_target_built"] is False
    summaries = {}
    logs = 0
    receipts = {}
    for path in own.rglob("report.json"):
        report = read(path)
        assert report["status"] == "pass", path
        receipts[str(path.relative_to(own))] = sha(path)
        for label, command in report.get("commands", {}).items():
            expected = command.get("sha256", command.get("output_sha256"))
            if expected is not None:
                assert sha(path.parent / (label + ".log")) == expected, (path, label)
                logs += 1
    for label, expected_count in [("first-order", 143), ("document", 160)]:
        report = read(own / label / "report.json")
        comparison = read(author / label / "report.json")
        assert len(report["declaration_axioms"]) == expected_count
        assert report["declaration_axioms"] == comparison["declaration_axioms"]
        assert report["facade_sources"] == comparison["facade_sources"]
        assert len(report["facade_sources"]) == 30
        assert report["temporary_builds_removed"] is True
        assert report["commands"]["lake-target"]["exit"] == 0
        control_key = "semantic_controls" if label == "first-order" else "accepted_controls"
        assert set(report[control_key]) == set(comparison[control_key])
        summaries[label] = {"audits": expected_count, "accepted_controls": list(report[control_key]),
                            "opt_in_lake_build": True, "facade_sources": 30}
        accepted = read(own / label / "accepted-regression/report.json")
        if label == "first-order":
            assert report["execution_rows_per_runner"] == 13
            assert len(report[control_key]) == 9
            assert len(accepted["kernel_cases"]) == 35
            assert len(accepted["malformed_documents"]) == 4
            summaries[label]["rows_per_runner"] = 13
            summaries[label]["runners"] = 3
        else:
            assert report["accepted_declaration_count"] == 156
            assert len(report["transferred_review_declarations"]) == 4
            assert report["runtime_profiles"] == comparison["runtime_profiles"]
            assert report["facade_controls"] == comparison["facade_controls"]
            assert len(report["facade_controls"]) == 4
            assert len(report[control_key]) == 7
            assert len(accepted["kernel_cases"]) == 20
            assert len(accepted["malformed_documents"]) == 8
            total = sum(len(p["rows"]) for p in report["runtime_profiles"].values())
            assert total == 25 and len(report["runtime_profiles"]) == 5
            summaries[label].update({"rows": total, "actual_files": 5,
                                    "facade_controls": report["facade_controls"],
                                    "review_declarations": report["transferred_review_declarations"]})
    assert not list(HERE.rglob("*.olean"))
    result = {"status": "pass", "source_manifest_sha256": sha(SOURCE / "SOURCE-ONLY.json"),
              "author_report_sha256": sha(SOURCE / "REPORT.md"),
              "receipts": receipts, "authenticated_command_logs": logs, "summaries": summaries,
              "author_audit_control_runtime_correspondence": True,
              "default_css_target_built": False, "compiled_outputs_retained": False}
    (HERE / "REPLAY-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "pass", "authenticated_command_logs": logs, "audits": [143, 160]}))


if __name__ == "__main__":
    main()
