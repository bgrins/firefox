# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gzip
import hashlib
import json
import os
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

try:
    import resource
except ImportError:
    resource = None


WORKLOADS = {
    "no-change": "Build again with a populated objdir and unchanged sources.",
    "image-alt-text": "Change the notification flag when updating image alt text.",
    "selector-invalidation": "Change the relative selector state reset in Stylo.",
    "quota-interface": "Add a failure category to the quota XPIDL interface.",
    "time-duration-header": "Add a debug accessor to the shared TimeDuration header.",
    "zucchini-library-flags": "Change a warning flag for the Zucchini C++ library.",
}
IMAGE_CALL = b"mImageContent->SetAttr(kNameSpaceID_None, nsGkAtoms::alt, errorMsg, "
COMPOUND_RESET = b"self.compound_state = PerCompoundState::new(index);"
QUOTA_LAST_CATEGORY = b"    CATEGORY_LOCAL_STORAGE_FLUSH = 1 << 4,\n"
DURATION_MIN_END = b"    return FromTicks(std::min(aA.mValue, aB.mValue));\n  }\n\n"
EDITS = {
    "image-alt-text": (
        Path("dom/html/ImageDocument.cpp"),
        IMAGE_CALL + b"true",
        IMAGE_CALL + b"false",
    ),
    "selector-invalidation": (
        Path("servo/components/style/invalidation/element/invalidation_map.rs"),
        COMPOUND_RESET
        + b"\n            self.compound_state_attributes = RelativeSelectorCompoundStateAttributes::new();",
        COMPOUND_RESET,
    ),
    "time-duration-header": (
        Path("mozglue/misc/TimeStamp.h"),
        DURATION_MIN_END + b" public:",
        DURATION_MIN_END
        + b"#if defined(DEBUG)\n  int64_t GetValue() const { return mValue; }\n#endif\n\n public:",
    ),
    "quota-interface": (
        Path("dom/quota/nsIQuotaArtificialFailure.idl"),
        QUOTA_LAST_CATEGORY + b"  };",
        QUOTA_LAST_CATEGORY + b"    CATEGORY_LOCAL_STORAGE_WRITE = 1 << 5,\n  };",
    ),
    "zucchini-library-flags": (
        Path("third_party/zucchini/moz.build"),
        b'CXXFLAGS += ["-Wno-pragma-clang-attribute"]',
        b'CXXFLAGS += ["-Wno-error=pragma-clang-attribute"]',
    ),
}
PROFILE_PREFIX = "Streaming resource usage profile to: "


def child_usage():
    if resource is None:
        return {}
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {
        "user_s": usage.ru_utime,
        "system_s": usage.ru_stime,
        "major_page_faults": usage.ru_majflt,
        "input_blocks": usage.ru_inblock,
        "output_blocks": usage.ru_oublock,
    }


def child_usage_since(before):
    return {key: value - before[key] for key, value in child_usage().items()}


def configuration(substs, env):
    keys = (
        "MOZ_BUILD_APP",
        "MOZ_ARTIFACT_BUILDS",
        "host",
        "target",
        "MOZ_DEBUG",
        "MOZ_OPTIMIZE",
        "MOZ_OPTIMIZE_FLAGS",
        "MOZ_PGO",
        "MOZ_PROFILE_GENERATE",
        "MOZ_PROFILE_USE",
        "CC",
        "CXX",
        "CC_VERSION",
        "HOST_CC",
        "HOST_CXX",
        "HOST_CC_VERSION",
        "RUSTC",
        "RUSTC_VERSION",
        "COMPILER_WRAPPER",
        "CCACHE",
        "MOZ_RUSTC_WRAPPER",
        "CARGO_INCREMENTAL",
    )
    config = {key: substs.get(key) for key in keys}
    if config["MOZ_BUILD_APP"] != "browser" or config["MOZ_ARTIFACT_BUILDS"]:
        raise ValueError("buildbench requires a configured native Firefox build")
    if config["MOZ_PGO"]:
        raise ValueError("buildbench requires a single-stage build; disable MOZ_PGO")
    if (
        config["CCACHE"]
        or config["COMPILER_WRAPPER"]
        or config["MOZ_RUSTC_WRAPPER"]
        or any(
            env.get(name)
            for name in (
                "RUSTC_WRAPPER",
                "RUSTC_WORKSPACE_WRAPPER",
                "CARGO_BUILD_RUSTC_WRAPPER",
                "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
            )
        )
    ):
        raise ValueError(
            "Disable compiler-result caching and compiler wrappers for buildbench"
        )
    for key in ("CC", "CXX", "HOST_CC", "HOST_CXX", "RUSTC"):
        command = config[key]
        if not command:
            raise ValueError(f"Missing configured {key}")
        if isinstance(command, str):
            if Path(command).is_file():
                command = [command]
            else:
                command = shlex.split(command, posix=os.name != "nt")
        executable = command[0].strip('"')
        resolved = shutil.which(executable) or executable
        if any(
            Path(p).stem.lower()
            in ("ccache", "sccache", "buildcache", "env", "distcc", "icecc")
            for p in (executable, Path(resolved).resolve())
        ):
            raise ValueError(f"{key} must invoke the compiler directly")
    config["environment_cargo_incremental"] = env.get("CARGO_INCREMENTAL")
    return config


def configured_build(source, objdir, mozconfig_path):
    path = objdir / "config.status.json"
    info_path = objdir / "mozinfo.json"
    if not path.is_file() or not info_path.is_file():
        raise ValueError("Run ./mach build to populate the objdir before benchmarking")
    info = json.loads(info_path.read_bytes())
    status = json.loads(path.read_bytes())
    for record in (info, status):
        for key, expected in (("topsrcdir", source), ("topobjdir", objdir)):
            if not record.get(key) or Path(record[key]).resolve() != expected:
                raise ValueError(f"Configured {key} does not match {expected}")
    configured_path = info.get("mozconfig")
    if (Path(configured_path).resolve() if configured_path else None) != (
        Path(mozconfig_path).resolve() if mozconfig_path else None
    ):
        raise ValueError("The objdir was configured with a different mozconfig")
    return configuration(status["substs"], os.environ)


def replace_bytes(path, expected, replacement, displaced):
    if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
        raise RuntimeError(f"Fixture changed: {path}")

    path.rename(displaced)
    try:
        if (
            displaced.is_symlink()
            or not displaced.is_file()
            or displaced.read_bytes() != expected
        ):
            raise RuntimeError(f"Fixture changed: {path}")
        os.link(replacement, path)
    except BaseException:
        if not os.path.lexists(path):
            os.link(displaced, path, follow_symlinks=False)
        raise


def read_fixture(source, workload):
    relative_path, before, after = EDITS[workload]
    path = source / relative_path
    if path.is_symlink():
        raise ValueError(f"Expected a regular source file at {path}")
    original = path.read_bytes()
    if b"\r\n" in original:
        before = before.replace(b"\n", b"\r\n")
        after = after.replace(b"\n", b"\r\n")
    if original.count(before) != 1:
        raise ValueError(f"Expected one {workload} fixture in {path}")
    return path, original, before, after


@contextmanager
def source_edit(source, output, workload, set_phase=lambda *args: None):
    path, original, before, after = read_fixture(source, workload)
    edited = original.replace(before, after)
    backup = output / f"{path.name}.original"
    backup.write_bytes(original)
    device = path.lstat().st_dev
    candidates = [source.parent, source / ".git", source / ".hg"]
    if output.is_relative_to(source):
        candidates.append(output)
    else:
        candidates.insert(0, output)
    for parent in candidates:
        if parent.is_dir() and parent.stat().st_dev == device:
            try:
                scratch = Path(tempfile.mkdtemp(prefix=".buildbench-", dir=parent))
                break
            except PermissionError:
                continue
    else:
        raise RuntimeError("Choose a writable --output on the fixture filesystem")
    replacement = scratch / "replacement"
    displaced = scratch / "original"
    removed = scratch / "edited"
    replacement.write_bytes(edited)
    replacement.chmod(stat.S_IMODE(path.stat().st_mode))
    set_phase("applying", scratch)
    replace_bytes(path, original, replacement, displaced)
    try:
        set_phase("applied", scratch)
        yield hashlib.sha256(edited).hexdigest()
    finally:
        set_phase("restoring", scratch)
        try:
            os.utime(displaced, None)
            replace_bytes(path, edited, displaced, removed)
            if path.read_bytes() != original:
                raise RuntimeError(f"Original changed: {path}")
        except (OSError, RuntimeError) as exc:
            raise RuntimeError(
                f"{exc}. Original saved at {backup}. Inspect displaced files in {scratch}"
            ) from exc
        removed.unlink()
        replacement.unlink()
        displaced.unlink()
        scratch.rmdir()
        set_phase(None)


def prepare_patch(source, output, patch):
    """Prepare a trusted patch. The measured build executes the patched checkout."""
    saved = output / "workload.patch"
    forward = Path(patch).read_bytes()
    saved.write_bytes(forward)
    env = dict(os.environ, GIT_INDEX_FILE=str(output / "patch.index"))
    env.setdefault("GIT_INDEX_VERSION", "4")

    def git(*args, stdin=None):
        proc = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", *args],
            cwd=source,
            env=env,
            input=stdin,
            capture_output=True,
            check=False,
        )
        if proc.returncode:
            message = proc.stderr.decode(errors="replace").strip()
            raise RuntimeError(message or f"git {args[0]} failed")
        return proc.stdout

    top = os.fsdecode(git("rev-parse", "--show-toplevel").removesuffix(b"\n"))
    if Path(top).resolve() != source.resolve():
        raise ValueError("Patch workloads require a Git checkout rooted at topsrcdir")
    base = git("rev-parse", "HEAD").decode("ascii").strip()
    git("read-tree", base)
    git("apply", "--cached", stdin=forward)
    restore = output / "restore.patch"
    inverse = git(
        "diff",
        "--cached",
        "--binary",
        "--no-renames",
        "--no-ext-diff",
        "--no-textconv",
        "--no-color",
        "--unified=3",
        "--src-prefix=a/",
        "--dst-prefix=b/",
        "-R",
        base,
        "--",
    )
    if inverse:
        restore.write_bytes(inverse)
    undo = () if inverse else ("--reverse",)
    reverse = inverse or forward
    postimage = git("write-tree").decode("ascii").strip()

    # Reverse numstat includes copy and rename sources; forward includes destinations.
    paths = set()
    for direction in ((), ("--reverse",)):
        stats = git("apply", "--numstat", "-z", *direction, stdin=forward)
        paths.update(row.split(b"\t", 2)[2] for row in stats.split(b"\0") if row)
    if b"CLOBBER" in paths:
        raise ValueError("Patch workload touches CLOBBER and requires a full build")
    paths = sorted(paths)

    def verify():
        for offset in range(0, len(paths), 32):
            batch = paths[offset : offset + 32]
            entries = git(
                "--literal-pathspecs", "ls-files", "--stage", "-z", "--", *batch
            )
            modes = {}
            for row in entries.split(b"\0"):
                if row:
                    entry, name = row.split(b"\t", 1)
                    modes[name] = entry.split()[0]
            present = []
            for name in batch:
                path = source / os.fsdecode(name)
                if any(
                    (source / parent).is_symlink()
                    for parent in Path(os.fsdecode(name)).parents
                ):
                    raise RuntimeError(f"Symlink in patch target path: {path}")
                mode = modes.get(name)
                try:
                    actual = path.lstat().st_mode
                except FileNotFoundError:
                    if mode is None:
                        continue
                    raise RuntimeError(f"Missing patch preimage: {path}") from None
                if not (
                    (mode in (b"100644", b"100755") and stat.S_ISREG(actual))
                    or (mode == b"120000" and stat.S_ISLNK(actual))
                ):
                    raise RuntimeError(f"Unexpected patch target: {path}")
                present.append(name)
            if present:
                git("--literal-pathspecs", "add", "--refresh", "--", *present)
                git("--literal-pathspecs", "diff-files", "--quiet", "--", *present)

    git("read-tree", base)
    verify()
    git("apply", "--check", stdin=forward)

    @contextmanager
    def edit(set_phase):
        verify()
        set_phase("applying")
        git("apply", stdin=forward)
        git("read-tree", postimage)
        verify()
        try:
            set_phase("applied")
            yield
        finally:
            set_phase("restoring")
            try:
                verify()
                git("apply", *undo, stdin=reverse)
                git("read-tree", base)
                verify()
            except RuntimeError as exc:
                recovery = restore if inverse else saved
                raise RuntimeError(
                    f"Could not restore the patch. Inspect {recovery}. {exc}"
                ) from exc
            set_phase(None)

    return edit, hashlib.sha256(forward).hexdigest()


def measure(source, output, label, jobs, *, objdir, mozconfig_path):
    log = output / f"{label}.log"
    command = [sys.executable, str(source / "mach"), "build", "-v"]
    if jobs:
        command += ["-j", str(jobs)]
    env = dict(
        os.environ, MOZ_OBJDIR=str(objdir), RUSTC_WRAPPER="", RUSTC_WORKSPACE_WRAPPER=""
    )
    if mozconfig_path:
        env["MOZCONFIG"] = str(mozconfig_path)
    else:
        env.pop("MOZCONFIG", None)
    env.pop("MOZ_RESOURCE_MONITOR_FORWARD", None)
    print(f"Running {label}. Log: {log}", flush=True)
    before = child_usage()
    start = time.monotonic()
    with log.open("wb") as stream:
        result = subprocess.run(
            command,
            cwd=objdir,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=False,
        )
    elapsed = time.monotonic() - start
    usage = child_usage_since(before)
    if result.returncode:
        raise RuntimeError(f"{label} exited {result.returncode}. See {log}")
    with log.open(errors="replace") as stream:
        paths = [
            line.partition(PROFILE_PREFIX)[2].strip()
            for line in stream
            if PROFILE_PREFIX in line
        ]
    if len(paths) != 1:
        raise RuntimeError(f"Expected one Mach build profile in {log}")
    profile = objdir / paths[0]
    saved = output / f"{label}.json.gz"
    with profile.open("rb") as original, gzip.open(saved, "wb") as compressed:
        shutil.copyfileobj(original, compressed)
    return {
        "wall_s": elapsed,
        "child_usage": usage,
        "profile": saved.name,
        "log": log.name,
        **profile_summary(saved),
    }


def profile_summary(saved):
    with gzip.open(saved, "rt") as stream:
        data = json.load(stream)
    markers = Counter()
    for thread in data["threads"]:
        table = thread["markers"]
        for index, end in zip(table["name"], table["endTime"], strict=True):
            name = thread["stringArray"][index]
            if end is not None and name in (
                "Object",
                "RustCrate",
                "xpt",
                "file_generate",
                "SharedLib",
                "Program",
            ):
                markers[name] += 1
    meta = data.get("meta", {})
    return {
        "completed_profile_markers": dict(markers),
        "profile_machine": {
            key: meta[key]
            for key in ("CPUName", "physicalCPUs", "logicalCPUs", "oscpu", "abi")
            if meta.get(key) is not None
        },
    }


def run(
    source,
    objdir,
    state,
    workload,
    repeat,
    jobs,
    metadata,
    output=None,
    patch=None,
    *,
    mozconfig=None,
):
    if repeat < 1 or jobs < 0:
        raise ValueError("repeat must be positive and jobs must be nonnegative")
    if (workload == "patch") != (patch is not None):
        raise ValueError("Specify either a named workload or a patch")
    source, objdir = source.resolve(), objdir.resolve()
    mozconfig = mozconfig or {}
    if "MOZ_PGO=1" in (mozconfig.get("configure_args") or ()):
        raise ValueError("buildbench requires a single-stage build; disable MOZ_PGO")
    mozconfig_path = (
        Path(mozconfig["path"]).absolute() if mozconfig.get("path") else None
    )
    config = configured_build(source, objdir, mozconfig_path)

    def mozconfig_digest():
        return (
            hashlib.sha256(mozconfig_path.read_bytes()).hexdigest()
            if mozconfig_path
            else None
        )

    initial_mozconfig = mozconfig_digest()
    if output is None:
        parent = state / "buildbench"
        parent.mkdir(exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix=f"{workload}-", dir=parent))
    else:
        output = Path(output).resolve()
        if output.is_relative_to(objdir.resolve()):
            raise ValueError(
                "Choose an output outside the objdir so it survives a clobber"
            )
        output.mkdir(parents=True, exist_ok=False)
    lock = state / "buildbench.lock"
    try:
        stream = lock.open("x")
    except FileExistsError:
        output.rmdir()
        raise ValueError(
            f"A buildbench run owns {lock}. See its recorded output directory."
        )
    with stream:
        stream.write(f"pid={os.getpid()}\n{output}\n")
    record = {
        **metadata,
        "configuration": config,
        "mozconfig_sha256": initial_mozconfig,
        "schema_version": 1,
        "workload": workload,
        "repeat": repeat,
        "jobs": jobs or "mach default",
        "platform": platform.platform(),
        "objdir": str(objdir),
        "filesystem_cache": "uncontrolled",
        "samples": [],
        "status": "running",
    }
    summary = output / "results.json"

    def save():
        tmp = summary.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, indent=2) + "\n")
        tmp.replace(summary)

    from mozbuild.controller.clobber import Clobberer

    clobberer = Clobberer(str(source), str(objdir))
    restore_summary_error = None

    def set_phase(phase, scratch=None):
        nonlocal restore_summary_error
        if phase is None:
            record.pop("recovery")
        else:
            record["recovery"] = {"phase": phase}
            if scratch is not None:
                record["recovery"]["directory"] = str(scratch)
        try:
            save()
        except OSError as exc:
            if phase not in ("restoring", None):
                raise
            # Finish rollback before reporting a summary error.
            if restore_summary_error is None:
                restore_summary_error = exc

    def sample(phase, trial=0):
        label = f"{trial}-{phase}" if trial else phase
        record["active_sample"] = {
            "phase": phase,
            "trial": trial,
            "log": f"{label}.log",
        }
        save()
        if mozconfig_digest() != initial_mozconfig:
            raise ValueError(f"The active mozconfig changed before {label}")
        if clobberer.clobber_needed():
            raise ValueError(
                f"A clobber is required before {label}. Cannot measure a rebuild."
            )
        row = measure(
            source, output, label, jobs, objdir=objdir, mozconfig_path=mozconfig_path
        )
        row.update(phase=phase, trial=trial)
        if (
            mozconfig_digest() != initial_mozconfig
            or configured_build(source, objdir, mozconfig_path) != config
        ):
            raise ValueError("Build configuration changed during measurement")
        record["samples"].append(row)
        del record["active_sample"]
        save()
        print(f"{label}  {row['wall_s']:.2f}s", flush=True)

    try:
        print(output, flush=True)
        save()
        if patch is not None:
            setup = record["patch_setup"] = {"status": "running"}
            save()
            print("Preparing the workload patch.", flush=True)
            before = child_usage()
            start = time.monotonic()
            try:
                edit, record["patch_sha256"] = prepare_patch(source, output, patch)
                setup["status"] = "complete"
            except BaseException:
                setup["status"] = "incomplete"
                raise
            finally:
                setup["wall_s"] = time.monotonic() - start
                setup["child_usage"] = child_usage_since(before)
        elif workload in EDITS:
            read_fixture(source, workload)
        sample("prepare")
        for trial in range(1, repeat + 1):
            if workload in EDITS or patch is not None:
                with (
                    edit(set_phase)
                    if patch is not None
                    else source_edit(source, output, workload, set_phase)
                ) as digest:
                    if workload in EDITS:
                        record["edited_path"] = EDITS[workload][0].as_posix()
                        record["edited_file_sha256"] = digest
                    sample("edit", trial)
                    sample("following-no-change", trial)
                if restore_summary_error is not None:
                    raise restore_summary_error
                sample("restore", trial)
            else:
                sample("no-change", trial)
        record["status"] = "complete"
    except BaseException as exc:
        record.update(status="incomplete", error=str(exc) or type(exc).__name__)
        raise
    finally:
        try:
            save()
        except OSError as exc:
            if record["status"] != "incomplete":
                raise
            print(f"Could not write {summary}: {exc}", file=sys.stderr)
        finally:
            if "recovery" not in record:
                (output / "patch.index").unlink(missing_ok=True)
                lock.unlink()
    return output
