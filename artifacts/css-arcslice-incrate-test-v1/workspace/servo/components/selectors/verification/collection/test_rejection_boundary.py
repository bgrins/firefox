#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import copy
import hashlib
import io
import json
import platform
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import rejection_boundary
import verify_rejection
from normalize import UnsupportedShape


def transcript():
    return "\n".join(
        f"'{name}' depends on axioms: [{', '.join(sorted(axioms))}]"
        if axioms else f"'{name}' does not depend on any axioms"
        for name, axioms in rejection_boundary.expected_audits().items()
    )


class AuditTests(unittest.TestCase):
    def test_exact_current_reports(self):
        self.assertEqual(len(rejection_boundary.expected_audits()), 64)
        rejection_boundary.audit_combined(transcript())

    def test_missing_duplicate_and_unknown_reports(self):
        text = transcript()
        lines = text.splitlines()
        for changed in ["", "\n".join(lines[1:]), text + "\n" + lines[0], text + "\n'extra' does not depend on any axioms", text.replace("local_name_no_false_rejection", "unrelated")]:
            with self.subTest(changed=changed):
                with self.assertRaises(UnsupportedShape):
                    rejection_boundary.audit_combined(changed)

    def test_forbidden_axioms(self):
        for axiom in ["sorryAx", "Lean.ofReduceBool", "collector_soundness"]:
            with self.subTest(axiom=axiom):
                with self.assertRaisesRegex(UnsupportedShape, "Unexpected axioms"):
                    rejection_boundary.audit_combined(transcript().replace("[", f"[{axiom}, ", 1))

    def test_manifest_count_and_axiom_limits(self):
        original = json.loads((rejection_boundary.PROJECT / "rejection-boundary.json").read_text())
        for change in ["count", "axiom"]:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                manifest = copy.deepcopy(original)
                name = next(iter(manifest["core_axioms"]))
                if change == "count":
                    del manifest["core_axioms"][name]
                else:
                    manifest["core_axioms"][name].append("sorryAx")
                (project / "rejection-boundary.json").write_text(json.dumps(manifest))
                with patch.object(rejection_boundary, "PROJECT", project):
                    with self.assertRaises(UnsupportedShape):
                        rejection_boundary.expected_audits()


class SourceInventoryTests(unittest.TestCase):
    scope = "matching"

    def test_source_digest_and_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            output = project / "generated" / self.scope / "model/Normalized"
            output.mkdir(parents=True)
            source = output / "Funs.lean"
            source.write_text("fresh source")
            manifest = {"lean_sources": {str(source.relative_to(project)): verify_rejection.digest(source)}}
            with patch.object(verify_rejection, "PROJECT", project):
                verify_rejection.validate_collection_sources(output, manifest, self.scope)
                source.write_text("changed source")
                with self.assertRaisesRegex(UnsupportedShape, "model changed"):
                    verify_rejection.validate_collection_sources(output, manifest, self.scope)
                source.write_text("fresh source")
                (output / "Unrecorded.lean").write_text("extra")
                with self.assertRaisesRegex(UnsupportedShape, "inventory changed"):
                    verify_rejection.validate_collection_sources(output, manifest, self.scope)
                with self.assertRaisesRegex(UnsupportedShape, "inventory changed"):
                    verify_rejection.validate_collection_sources(output, {"lean_sources": {}}, self.scope)


class ReleaseTests(unittest.TestCase):
    def test_release_archive_and_executable_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            tools = Path(directory)
            (tools / "aeneas").mkdir()
            archive = tools / "release.tar.gz"
            with tarfile.open(archive, "w:gz") as bundle:
                for name in ["aeneas", "charon"]:
                    data = name.encode()
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    bundle.addfile(info, io.BytesIO(data))
                    (tools / "aeneas" / name).write_bytes(data)
            asset = {"aeneas": archive.name, "aeneas_sha256": verify_rejection.digest(archive)}
            with patch.object(verify_rejection, "TOOLS", tools):
                verify_rejection.validate_release(asset)
                for name in ["aeneas", "charon"]:
                    with self.subTest(executable=name):
                        (tools / "aeneas" / name).write_bytes(b"changed")
                        with self.assertRaisesRegex(UnsupportedShape, "Release executable changed"):
                            verify_rejection.validate_release(asset)
                        (tools / "aeneas" / name).write_bytes(name.encode())
                asset["aeneas_sha256"] = hashlib.sha256(b"wrong archive").hexdigest()
                with self.assertRaisesRegex(UnsupportedShape, "archive changed"):
                    verify_rejection.validate_release(asset)

    def test_ambiguous_executable_entries(self):
        for entry_names in [["aeneas", "aeneas", "charon"], ["charon"]]:
            with self.subTest(entries=entry_names), tempfile.TemporaryDirectory() as directory:
                tools = Path(directory)
                archive = tools / "release.tar.gz"
                with tarfile.open(archive, "w:gz") as bundle:
                    for name in entry_names:
                        info = tarfile.TarInfo(name)
                        info.size = 1
                        bundle.addfile(info, io.BytesIO(b"x"))
                asset = {"aeneas": archive.name, "aeneas_sha256": verify_rejection.digest(archive)}
                with patch.object(verify_rejection, "TOOLS", tools):
                    with self.assertRaisesRegex(UnsupportedShape, "executable entry"):
                        verify_rejection.validate_release(asset)


class FreshnessTests(unittest.TestCase):
    scope = "matching"
    target = "rejection"

    def test_failed_provenance_removes_evidence_and_compiled_model(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            generated = project / "generated" / self.target
            model = generated / "model"
            model.mkdir(parents=True)
            evidence = generated / "evidence.json"
            evidence.write_text("stale success")
            stale = model / "Stale.olean"
            stale.write_text("stale compiled proof")
            with patch.object(verify_rejection, "PROJECT", project), patch.object(verify_rejection, "validate_tools", side_effect=RuntimeError("changed tool")):
                with self.assertRaisesRegex(RuntimeError, "changed tool"):
                    verify_rejection.main(self.scope)
            self.assertFalse(evidence.exists())
            self.assertFalse(stale.exists())

    def test_failed_core_regeneration_removes_old_core_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "collection"
            project.mkdir()
            host = f"{platform.system()}-{platform.machine()}"
            (root / "toolchain.json").write_text(json.dumps({"platforms": {host: {}}}))
            stale = [root / "generated/stylo_bloom_verification.llbc", root / "lean/Generated/StyloBloomVerification.lean"]
            for path in stale:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale")
            with patch.object(verify_rejection, "PROJECT", project), patch.object(verify_rejection, "TOOLS", root), patch.object(verify_rejection, "validate_tools"), patch.object(verify_rejection, "validate_release"), patch.object(verify_rejection.subprocess, "run", side_effect=RuntimeError("extraction failed")):
                with self.assertRaisesRegex(RuntimeError, "extraction failed"):
                    verify_rejection.main(self.scope)
            self.assertTrue(all(not path.exists() for path in stale))
            self.assertFalse((project / "generated" / self.target / "evidence.json").exists())

    def test_failed_compilation_cannot_reuse_success_or_oleans(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "collection"
            matching = project / "generated" / self.scope / "model/Normalized"
            matching.mkdir(parents=True)
            (matching / "Funs.lean").write_text("fresh matching source")
            (matching / "Funs.olean").write_text("untrusted compiled dependency")
            manifest = {"lean_sources": {str((matching / "Funs.lean").relative_to(project)): verify_rejection.digest(matching / "Funs.lean")}}
            (project / "generated" / self.scope / "evidence.json").write_text(json.dumps(manifest))
            evidence = project / "generated" / self.target / "evidence.json"
            evidence.parent.mkdir()
            evidence.write_text("old success")
            for name in ["BloomProofs", "PackingProofs", "NormalizationProofs"]:
                proof = root / "lean" / f"{name}.lean"
                proof.parent.mkdir(exist_ok=True)
                proof.write_text("fresh proof")
            proof = project / "lean" / self.scope / "RejectionProofs.lean"
            proof.parent.mkdir(parents=True)
            proof.write_text("fresh bridge")
            (project / "lean/PackingBridgeProofs.lean").write_text("fresh shared bridge")
            host = f"{platform.system()}-{platform.machine()}"
            (root / "toolchain.json").write_text(json.dumps({"platforms": {host: {"lean": "test.tar.zst"}}}))

            def run(command, **kwargs):
                if command[0] == verify_rejection.sys.executable:
                    core_model = root / "lean/Generated/StyloBloomVerification.lean"
                    core_model.parent.mkdir(exist_ok=True)
                    core_model.write_text("fresh extracted source")
                    return subprocess.CompletedProcess(command, 0)
                return subprocess.CompletedProcess(command, 1, stdout="proof failed")

            with patch.object(verify_rejection, "PROJECT", project), patch.object(verify_rejection, "TOOLS", root), patch.object(verify_rejection, "validate_tools"), patch.object(verify_rejection, "validate_release"), patch.object(verify_rejection.subprocess, "run", side_effect=run), patch.object(verify_rejection.subprocess, "check_output", return_value="dependencies"):
                with self.assertRaises(subprocess.CalledProcessError):
                    verify_rejection.main(self.scope)
            self.assertFalse(evidence.exists())
            self.assertFalse((evidence.parent / "model/Normalized/Funs.olean").exists())


if __name__ == "__main__":
    unittest.main()
