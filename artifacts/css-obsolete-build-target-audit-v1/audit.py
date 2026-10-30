import collections
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/css-spec-lean"
REVIEW = BASE / ".lake/research-review"
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
paired = {
    "anonymous-layer-candidate-v1": "e2ee3de",
    "global-condition-candidate-v2": "13c41ee",
    "import-layer-candidate-v1": "b818a9a",
    "rollback-layer-candidate-v1": "0f1f56b",
    "author-sheets-candidate-v1": "ee116c8",
}
names = ["0f1f56b", "13c41ee", "7f23946", "b818a9a", "e2ee3de", "ee116c8", "fba53c4-retry-v2", "global-condition-candidate-v1", *paired]
rows = []
for name in names:
    target = REVIEW / name / ".lake/build"
    assert target.is_dir() and not target.is_symlink()
    stat = target.stat()
    allocated = apparent = count = 0
    extensions = collections.Counter()
    links, unexpected = [], []
    for current, dirs, files in os.walk(target, followlinks=False):
        for directory in list(dirs):
            if (Path(current) / directory).is_symlink():
                links.append(str(Path(current) / directory))
                dirs.remove(directory)
        for filename in files:
            path = Path(current) / filename
            stat_file = path.lstat()
            if path.is_symlink():
                links.append(str(path))
                continue
            allocated += stat_file.st_blocks * 512
            apparent += stat_file.st_size
            count += 1
            extensions[path.suffix] += 1
            if path.suffix not in {".hash", ".json", ".c", ".ilean", ".olean", ".trace"} or (path.suffix == ".json" and not path.name.endswith(".setup.json")):
                unexpected.append(str(path.relative_to(target)))
    row = {"target": str(target.relative_to(ROOT)), "identity": [stat.st_dev, stat.st_ino],
           "allocated_file_bytes": allocated, "apparent_file_bytes": apparent, "file_count": count,
           "extensions": dict(extensions), "symlinks": links, "unexpected_files": unexpected,
           "eligible_after_fresh_root_checks": False}
    process_path = REVIEW / (name + "-process.json")
    process = read(process_path)
    row["recorded_completed_exit_code"] = process["completed_exit_code"]
    if process["completed_exit_code"] != 0:
        row["excluded_reason"] = "Interrupted historical verification, no successful terminal; preserved conservatively."
        rows.append(row)
        continue
    binding_path = REVIEW / (name + "-binding.json")
    binding = read(binding_path)
    assert binding["completed_exit_code"] == 0 and not links and not unexpected
    archive_name = paired.get(name, name)
    archive_binding_path = REVIEW / (archive_name + "-binding.json")
    accepted = read(archive_binding_path)
    assert accepted["status"] == "accepted" and accepted["completed_exit_code"] == 0
    assert accepted["producer_sha256"] == binding["producer_sha256"]
    report_key = "copy_report" if "copy_report" in binding else "archive_report"
    report = BASE / binding[report_key]
    assert sha(report) == binding[report_key + "_sha256"]
    archive_report = BASE / accepted["archive_report"]
    assert sha(archive_report) == accepted["archive_report_sha256"]
    first, second = read(report), read(archive_report)
    assert all(first[key] == second[key] for key in accepted["equal_vectors"])
    tar_name = "fba53c4" if archive_name == "fba53c4-retry-v2" else archive_name
    archive = REVIEW / (tar_name + "-source.tar")
    assert sha(archive) == accepted["archive_sha256"]
    source = REVIEW / (name + "-source.json")
    assert source.is_file()
    log = REVIEW / (name + (".log" if name in paired else "-check.log"))
    assert log.is_file() and "PASS:" in log.read_text()
    retained = {str(f.relative_to(ROOT)): {"sha256": sha(f), "bytes": f.stat().st_size}
                for f in {binding_path, process_path, source, report, archive_binding_path, archive_report, archive, log}}
    assert all(not (ROOT / path).is_relative_to(target) for path in retained)
    row.update(eligible_after_fresh_root_checks=True, owner_session_id=binding["session_id"],
               accepted_archive_commit=accepted["commit"], retained_evidence=retained,
               archive_report_vectors_match=True, no_remaining_build_product_dependency="Completed accepted verification; source archive, report and logs retained outside target. Cache contains only rebuildable compiler outputs.")
    rows.append(row)
metadata = {}
for name in ("lakefile.lean", "lake-manifest.json"):
    path = BASE / name
    assert "research-review" not in path.read_text()
    metadata[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
result = {"status": "read-only audit; no deletion performed", "targets": rows,
          "eligible_allocated_file_bytes": sum(r["allocated_file_bytes"] for r in rows if r["eligible_after_fresh_root_checks"]),
          "canonical_dependency_declarations_have_no_research_review_reference": metadata,
          "excluded": ["original fba53c4 cache", "canonical .lake/build and .lake/packages", "toolchains and Creusot target", "main objdir-full.noindex", "active browser candidate/runtime/backups"],
          "preconditions": ["Root rechecks no active process cwd/open files/command targets any selected path before deletion.", "Root reauthenticates identities, compiler-only/no-symlink contents and retained evidence immediately before deletion.", "Remove only each exact .lake/build directory, never source, verification, archive or dependency parents."],
          "already_removed": {"isolated_servo_targets": 5, "prior_lean_review_targets": 198},
          "no_source_git_epoch_app_deletion_mutation": True}
(OUT / "REPORT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"eligible_targets": sum(r["eligible_after_fresh_root_checks"] for r in rows), "eligible_allocated_file_bytes": result["eligible_allocated_file_bytes"], "report_sha256": sha(OUT / "REPORT.json")}))
