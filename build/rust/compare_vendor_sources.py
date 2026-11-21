# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Compare Cargo's full vendor directory with one directory per locked Git source."""

import argparse
import difflib
import hashlib
import json
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from statistics import median

def native_commands(src, obj, work):
    sys.path.insert(0, str(src / "python/mozbuild"))
    from mozbuild.rust_commands import (
        CargoInvocation,
        compose_cargo_build_edge_argv,
        compose_env,
        load_cargo_spec,
    )

    spec = json.loads(
        (obj / "toolkit/library/rust/.cargo-library-spec.json").read_bytes()
    )
    cmd, cfg, topsrcdir, topobjdir = load_cargo_spec(spec)
    if Path(topsrcdir).resolve() != src or Path(topobjdir).resolve() != obj:
        raise ValueError(
            "The native Cargo command spec must belong to these directories"
        )
    inv = CargoInvocation()
    env = compose_env(cmd, cfg, os.environ, inv, topsrcdir, topobjdir)
    env.update(
        CARGO_TARGET_DIR=str(work / "target"), CARGO_HOME=str(work / "cargo-home")
    )
    cargo = cfg.get("CARGO")
    commands = {
        "metadata": [
            cargo,
            "metadata",
            "--format-version",
            "1",
            "--all-features",
            "--frozen",
            "--manifest-path",
            cmd.manifest_path,
        ],
        "gkrust-unit-graph": compose_cargo_build_edge_argv(cmd, cfg, inv),
    }
    commands["gkrust-unit-graph"][2:2] = ["-Zunstable-options", "--unit-graph"]
    envs = {"metadata": env, "gkrust-unit-graph": dict(env, RUSTC_BOOTSTRAP="1")}
    return commands, envs


def git_source_views(metadata, root, shared=False):
    groups = {}
    for package in metadata["packages"]:
        source = package.get("source") or ""
        if source.startswith("git+"):
            key = source.rsplit("#", 1)[0]
            groups.setdefault(key, []).append(Path(package["manifest_path"]).parent)
    if not groups:
        raise ValueError("Cargo metadata has no Git packages")
    replacements = {}
    aliases = {}
    for source, packages in sorted(groups.items()):
        name = (
            "git-packages" if shared
            else "git-" + hashlib.sha256(source.encode()).hexdigest()[:16]
        )
        directory = root / name
        directory.mkdir(exist_ok=shared)
        for package in packages:
            link = directory / package.name
            if aliases.get(str(link)) == str(package):
                continue
            link.symlink_to(package, target_is_directory=True)
            aliases[str(link)] = str(package)
        replacements[source] = (name, directory)
    return replacements, aliases


def replace_sources(config, replacements):
    sections = config.splitlines(keepends=True)
    for source, (name, directory) in replacements.items():
        index = sections.index(f'[source."{source}"]\n')
        for line in range(index + 1, len(sections)):
            if sections[line].startswith("["):
                raise ValueError(f"No replacement for {source}")
            if sections[line] == 'replace-with = "vendored-sources"\n':
                sections[line] = f'replace-with = "{name}"\n'
                break
        else:
            raise ValueError(f"No replacement for {source}")
    for name, directory in dict.fromkeys(replacements.values()):
        sections.append(
            f"\n[source.{name}]\ndirectory = {json.dumps(str(directory))}\n"
        )
    return "".join(sections)


def normalize_paths(output, aliases):
    text = output.decode()
    for link, original in aliases.items():
        text = text.replace('"' + link + "/", '"' + original + "/")
        text = text.replace('"' + link + '"', '"' + original + '"')
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("objdir", type=Path)
    parser.add_argument("--repeat", type=int, default=6)
    parser.add_argument("--output-parent", type=Path)
    parser.add_argument(
        "--shared-git-directory",
        action="store_true",
        help="Put all locked Git packages in one directory with a common source-path prefix.",
    )
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    src, obj = args.source.resolve(), args.objdir.resolve()
    work = Path(
        tempfile.mkdtemp(prefix="cargo-sources-", dir=args.output_parent)
    ).resolve()
    print(work, flush=True)
    commands, envs = native_commands(src, obj, work)
    cargo = commands["metadata"][0]
    config = (obj / ".cargo/config.toml").read_text()
    cf = work / ".cargo/config.toml"
    cf.parent.mkdir()
    cf.write_text(config)

    def invoke(kind):
        return subprocess.check_output(commands[kind], cwd=work, env=envs[kind])

    reference = {kind: json.loads(invoke(kind)) for kind in commands}
    views, aliases = git_source_views(
        reference["metadata"], work, args.shared_git_directory
    )
    configs = {"base": config, "candidate": replace_sources(config, views)}
    template = ".cargo/config.toml.in"
    base = (src / template).read_text()
    patch = difflib.unified_diff(
        base.splitlines(True),
        replace_sources(base, views).splitlines(True),
        f"a/{template}",
        f"b/{template}",
    )
    (work / "candidate.patch").write_text("".join(patch))
    result = {
        "revision": subprocess.check_output(
            ["git", "-C", src, "rev-parse", "HEAD"], text=True
        ).strip(),
        "cargo": subprocess.check_output([cargo, "--version"], text=True).strip(),
        "git_sources": len(views),
        "git_directories": len(set(views.values())),
        "git_packages": len(aliases),
        "units": len(reference["gkrust-unit-graph"]["units"]),
        "edges": sum(
            len(u["dependencies"]) for u in reference["gkrust-unit-graph"]["units"]
        ),
        "pairs": [],
    }
    print({k: v for k, v in result.items() if k != "pairs"}, flush=True)
    for trial in range(1, args.repeat + 1):
        row = {"trial": trial}
        for arm in configs if trial % 2 else reversed(configs):
            cf.write_text(configs[arm])
            for kind in commands:
                start = time.monotonic()
                raw = invoke(kind)
                row.setdefault(kind, {})[arm] = time.monotonic() - start
                if normalize_paths(raw, aliases) != reference[kind]:
                    raise ValueError(f"Different {kind} for {arm} trial {trial}")
        result["pairs"].append(row)
        print(row, flush=True)
        (work / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    for kind in commands:
        print(
            kind,
            "median paired saving",
            median(
                row[kind]["base"] - row[kind]["candidate"] for row in result["pairs"]
            ),
        )


if __name__ == "__main__":
    main()
