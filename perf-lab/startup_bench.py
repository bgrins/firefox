#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Startup time / memory benchmark harness for SLIM_UI experiments.

Run under mach so the marionette + mozrunner packages are importable:

    ./mach python perf-lab/startup_bench.py run --label baseline --runs 10
    ./mach python perf-lab/startup_bench.py run --label slim --runs 10 --pref-set slim
    ./mach python perf-lab/startup_bench.py compare baseline slim
    ./mach python perf-lab/startup_bench.py memdiff baseline slim

The most useful signal here is not the timing (noisy) but the ES module
list diff, which is deterministic: it says exactly which modules a variant
avoided loading.
"""

import argparse
import json
import os
import shutil
import statistics
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PRESETS = HERE / "presets"
MEMREPORTS = HERE / "memory"

# What `mach firefox-devtools-mcp` effectively launches with today:
# .mcp.json passes --pref remote.prefs.recommended=false and
# --pref browser.smartwindow.enabled=true; the MCP package then adds
# app.update.disabledForTesting=true because recommended prefs are off.
MCP_PREFS = {
    "remote.prefs.recommended": False,
    "browser.smartwindow.enabled": True,
    "app.update.disabledForTesting": True,
}

# Measured in the parent process, chrome context, once the session is live.
MEASURE = r"""
const done = arguments[arguments.length - 1];
(async () => {
  const out = {};

  const info = Services.startup.getStartupInfo();
  out.startupInfo = {};
  for (const [key, value] of Object.entries(info)) {
    out.startupInfo[key] = value instanceof Date ? value.getTime() : value;
  }

  const mgr = Cc["@mozilla.org/memory-reporter-manager;1"].getService(
    Ci.nsIMemoryReporterManager
  );
  out.mem = {};
  for (const key of [
    "resident",
    "residentUnique",
    "residentPeak",
    "heapAllocated",
    "vsize",
    "JSMainRuntimeGCHeap",
    "JSMainRuntimeRealmsSystem",
    "JSMainRuntimeRealmsUser",
    "storageSQLite",
    "imagesContentUsedUncompressed",
  ]) {
    try {
      out.mem[key] = mgr[key];
    } catch (e) {
      out.mem[key] = null;
    }
  }

  // The startup work dispatched via BrowserUtils.callModulesFromCategory. This is
  // the authoritative list of what runs at startup, and the names here are the
  // exact _descriptiveName keys a SLIM_UI gate would filter on.
  out.categories = {};
  for (const cat of [
    "browser-before-ui-startup",
    "browser-first-window-ready",
    "browser-idle-startup",
    "browser-best-effort-idle-startup",
    "browser-window-before-initial-xul-layout-document-preparation",
    "browser-window-before-initial-xul-layout",
    "browser-window-domcontentloaded-before-tabbrowser",
    "browser-window-domcontentloaded-tabbrowser",
    "browser-window-domcontentloaded",
    "browser-window-load-before-sessionstore-init",
    "browser-window-load",
    "browser-window-delayed-startup",
    "browser-window-sessionstore-initialized",
  ]) {
    try {
      out.categories[cat] = Array.from(
        Services.catMan.enumerateCategory(cat),
        e => `${e.data}|${e.value}`
      );
    } catch (e) {
      out.categories[cat] = [];
    }
  }

  // Reported by the SLIM_UI gate, so we can verify the skip list actually matched
  // instead of silently no-opping on a typo'd entry name.
  out.slimUIPrefs = {};
  try {
    out.slimUIPrefs.enabled = Services.prefs.getBoolPref(
      "browser.slimui.enabled",
      false
    );
    out.slimUIPrefs.skip = Services.prefs.getCharPref("browser.slimui.skip", "");
  } catch (e) {
    out.slimUIPrefs = { error: String(e) };
  }

  try {
    const { BrowserUtils } = ChromeUtils.importESModule(
      "resource://gre/modules/BrowserUtils.sys.mjs"
    );
    out.hasSlimUIGetter = "slimUIReport" in BrowserUtils;
    out.slimUI = BrowserUtils.slimUIReport ?? null;
  } catch (e) {
    out.hasSlimUIGetter = `<error: ${e}>`;
    out.slimUI = null;
  }

  try {
    out.esModules = Cu.loadedESModules;
  } catch (e) {
    out.esModules = [];
  }
  try {
    out.jsModules = Cu.loadedModules;
  } catch (e) {
    out.jsModules = [];
  }

  try {
    const info = await ChromeUtils.requestProcInfo();
    out.procs = {
      parent: { type: info.type, memory: info.memory, cpuTime: info.cpuTime },
      children: info.children.map(c => ({
        type: c.type,
        memory: c.memory,
        cpuTime: c.cpuTime,
      })),
    };
  } catch (e) {
    out.procs = null;
  }

  done(out);
})();
"""

# Metrics surfaced by `compare`, in report order. (key, label, unit)
METRICS = [
    ("t.main", "main", "ms"),
    ("t.createTopLevelWindow", "createTopLevelWindow", "ms"),
    ("t.firstPaint", "firstPaint", "ms"),
    ("t.firstPaint2", "firstPaint2", "ms"),
    ("t.firstLoadURI", "firstLoadURI", "ms"),
    ("t.sessionRestored", "sessionRestored", "ms"),
    ("wall_ms", "wall (spawn->session)", "ms"),
    ("early.esModuleCount", "ES modules @early", "count"),
    ("settled.esModuleCount", "ES modules @settled", "count"),
    ("early.mem.residentUnique", "USS parent @early", "bytes"),
    ("settled.mem.residentUnique", "USS parent @settled", "bytes"),
    ("settled.mem.heapAllocated", "heap parent @settled", "bytes"),
    ("settled.mem.JSMainRuntimeGCHeap", "JS GC heap @settled", "bytes"),
    ("settled.mem.JSMainRuntimeRealmsSystem", "system realms @settled", "count"),
    ("settled.procs.total", "RSS all procs @settled", "bytes"),
    ("settled.procs.count", "process count @settled", "count"),
]


def dig(obj, dotted):
    for part in dotted.split("."):
        if obj is None:
            return None
        obj = obj.get(part) if isinstance(obj, dict) else None
    return obj


def find_binary():
    if os.environ.get("SLIM_UI_BENCH_BINARY"):
        return Path(os.environ["SLIM_UI_BENCH_BINARY"])
    try:
        from mozbuild.base import MozbuildObject

        build = MozbuildObject.from_environment()
        return Path(build.get_binary_path())
    except Exception as exc:
        sys.exit(f"could not locate firefox binary: {exc}\nSet SLIM_UI_BENCH_BINARY.")


def summarize_procs(procs):
    """Collapse requestProcInfo output into total RSS and a process count."""
    if not procs:
        return None
    parent = procs.get("parent") or {}
    children = procs.get("children") or []
    total = (parent.get("memory") or 0) + sum(c.get("memory") or 0 for c in children)
    by_type = {}
    for child in children:
        entry = by_type.setdefault(
            child.get("type") or "unknown", {"n": 0, "memory": 0}
        )
        entry["n"] += 1
        entry["memory"] += child.get("memory") or 0
    return {
        "total": total,
        "count": 1 + len(children),
        "parent": parent.get("memory"),
        "byType": by_type,
    }


def snapshot(marionette):
    from marionette_driver.marionette import Marionette  # noqa: F401

    with marionette.using_context("chrome"):
        raw = marionette.execute_async_script(MEASURE, script_timeout=60000)
    return {
        "mem": raw.get("mem") or {},
        "esModuleCount": len(raw.get("esModules") or []),
        "jsModuleCount": len(raw.get("jsModules") or []),
        "esModules": raw.get("esModules") or [],
        "jsModules": raw.get("jsModules") or [],
        "procs": summarize_procs(raw.get("procs")),
        "startupInfo": raw.get("startupInfo") or {},
        "categories": raw.get("categories") or {},
        "slimUI": raw.get("slimUI"),
        "slimUIPrefs": raw.get("slimUIPrefs") or {},
        "hasSlimUIGetter": raw.get("hasSlimUIGetter"),
    }


DUMP_MEMORY = r"""
const done = arguments[arguments.length - 1];
Cc["@mozilla.org/memory-info-dumper;1"]
  .getService(Ci.nsIMemoryInfoDumper)
  .dumpMemoryReportsToNamedFile(
    arguments[0],
    () => done(true),
    null,
    /* anonymize */ false,
    /* minimizeMemoryUsage */ false
  );
"""


def dump_memory_report(marionette, path):
    """Full about:memory tree (gzipped JSON) for per-path attribution."""
    with marionette.using_context("chrome"):
        marionette.execute_async_script(
            DUMP_MEMORY, script_args=[str(path)], script_timeout=120000
        )


# Marionette's Python client forces ~120 prefs of its own (geckoinstance.py
# required_prefs + desktop_prefs) and sets remote.prefs.recommended=False. That is
# NOT what `mach firefox-devtools-mcp` gets -- it launches through geckodriver,
# whose pref set (testing/geckodriver/src/prefs.rs DEFAULT) is much smaller. Left
# alone, the harness would silently pre-disable much of what we want to measure.
# So we replace the client's pref dicts with the chosen baseline, keeping only what
# Marionette needs to stay usable as a measurement channel.
MARIONETTE_ESSENTIAL_PREFS = {
    "dom.max_chrome_script_run_time": 0,
    "dom.max_script_run_time": 0,
    "browser.dom.window.dump.enabled": True,
    "devtools.console.stdout.chrome": True,
    "focusmanager.testmode": True,
    "toolkit.startup.max_resumed_crashes": -1,
    "browser.sessionstore.resume_from_crash": False,
    "browser.shell.checkDefaultBrowser": False,
    "browser.warnOnQuit": False,
    "browser.tabs.warnOnClose": False,
    "browser.tabs.warnOnCloseOtherTabs": False,
}


def free_port():
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def build_prefs(args, port):
    """Assemble the complete pref set for a run. We write these ourselves rather
    than letting GeckoInstance do it, so the pref state is explicit and matches
    the MCP launch instead of the Marionette client's much larger forced set."""
    prefs = {}
    if args.pref_baseline == "marionette":
        from marionette_driver import geckoinstance

        prefs.update(geckoinstance.GeckoInstance.required_prefs)
        prefs.update(geckoinstance.DesktopInstance.desktop_prefs)
    else:
        prefs.update(MARIONETTE_ESSENTIAL_PREFS)
        if args.pref_baseline == "geckodriver":
            prefs.update(json.loads((PRESETS / "geckodriver-default.json").read_text()))
        prefs["remote.prefs.recommended"] = False

    if args.mcp_prefs:
        prefs.update(MCP_PREFS)
    prefs["browser.startup.page"] = 0
    prefs["browser.startup.homepage"] = args.home

    for name in args.pref_set:
        path = name if os.path.sep in name else str(PRESETS / f"{name}.json")
        try:
            prefs.update(json.loads(Path(path).read_text()))
        except FileNotFoundError:
            available = sorted(p.stem for p in PRESETS.glob("*.json"))
            sys.exit(f"unknown pref set {name!r}; available: {', '.join(available)}")

    for item in args.pref:
        key, _, value = item.partition("=")
        if value in ("true", "false"):
            prefs[key] = value == "true"
        else:
            try:
                prefs[key] = int(value)
            except ValueError:
                prefs[key] = value

    prefs.pop("_comment", None)
    prefs["marionette.port"] = port
    prefs["marionette.defaultPrefs.port"] = port
    return prefs


def make_profile(template, prefs, purge_cache):
    """Clone the template profile and, unless told otherwise, drop its JS startup
    cache.

    This matters more than it looks: `mach build faster` does not bump the
    BuildID, so Gecko treats a cloned scriptCache.bin as valid and happily runs
    the *previous* build's bytecode. Without purging, a frontend change measures
    as a perfect no-op.
    """
    from mozprofile import Profile

    clone = tempfile.mkdtemp(prefix="slimbench-")
    if template:
        os.rmdir(clone)  # Profile.clone requires the target not to exist
        profile = Profile.clone(
            path_from=template, path_to=clone, preferences=prefs, restore=False
        )
    else:
        profile = Profile(profile=clone, preferences=prefs, restore=False)

    if purge_cache:
        shutil.rmtree(Path(profile.profile) / "startupCache", ignore_errors=True)
    return profile


def single_run(args, binary, env_overrides, run_index):
    from marionette_driver.marionette import Marionette

    port = free_port()
    prefs = build_prefs(args, port)
    profile = make_profile(args.profile_template, prefs, args.purge_cache)

    # GeckoInstance copies os.environ at launch, so overrides go there.
    saved = {k: os.environ.get(k) for k in env_overrides}
    os.environ.update(env_overrides)

    gecko_log = str(HERE / "gecko.log") if args.gecko_log else "-"
    started = time.monotonic()
    marionette = None
    try:
        marionette = Marionette(
            bin=str(binary),
            port=port,
            profile=profile,
            headless=args.headless,
            gecko_log=gecko_log,
            app_args=["-no-remote"],
            startup_timeout=120,
        )
        marionette.start_session()
        wall_ms = (time.monotonic() - started) * 1000.0

        early = snapshot(marionette)
        if args.settle > 0:
            time.sleep(args.settle)
            settled = snapshot(marionette)
        else:
            settled = early

        if args.memory_report and run_index == 0:
            MEMREPORTS.mkdir(parents=True, exist_ok=True)
            dump_memory_report(marionette, MEMREPORTS / f"{args.label}-memory.json.gz")

        # Late events (firstPaint2, sessionRestored) may not be stamped yet at
        # the early snapshot, so prefer the settled one for timings.
        info = settled["startupInfo"] or early["startupInfo"]
        if "firstPaint2" not in info and "firstPaint2" in early["startupInfo"]:
            info = early["startupInfo"]
        process_t = info.get("process")
        timings = {}
        if process_t:
            for key, value in info.items():
                if key != "process" and isinstance(value, (int, float)):
                    timings[key] = value - process_t

        return {
            "index": run_index,
            "wall_ms": wall_ms,
            "t": timings,
            "early": {
                k: v for k, v in early.items() if k not in ("esModules", "jsModules")
            },
            "settled": {
                k: v for k, v in settled.items() if k not in ("esModules", "jsModules")
            },
            "_esModules": settled["esModules"],
            "_jsModules": settled["jsModules"],
        }
    finally:
        if marionette is not None:
            try:
                marionette.cleanup()
            except Exception:
                pass
        try:
            shutil.rmtree(profile.profile, ignore_errors=True)
        except Exception:
            pass
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def resolve_profile_template(args, binary):
    """Default to the profile mach firefox-devtools-mcp reuses, so the run starts
    from a warm profile rather than paying one-time first-run costs."""
    if args.profile_template == "none":
        return None
    if args.profile_template:
        return args.profile_template
    # binary is <objdir>/dist/Nightly.app/Contents/MacOS/firefox
    for parent in binary.parents:
        candidate = parent / "tmp" / "profile-default"
        if candidate.is_dir():
            return str(candidate)
    return None


def cmd_run(args):
    binary = find_binary()
    if not binary.exists():
        sys.exit(f"binary not found: {binary}")
    args.profile_template = resolve_profile_template(args, binary)
    print(f"profile: {args.profile_template or '(fresh)'}")
    print(f"baseline: {args.pref_baseline} prefs")

    env_overrides = {}
    for item in args.env:
        key, _, value = item.partition("=")
        env_overrides[key] = value or "1"

    RESULTS.mkdir(parents=True, exist_ok=True)
    total = args.runs + args.warmup
    runs = []
    modules = {"esModules": [], "jsModules": []}

    print(f"binary : {binary}")
    print(f"env    : {env_overrides or '(none)'}")
    print(f"runs   : {args.runs} (+{args.warmup} warmup), settle {args.settle}s")
    print()

    for i in range(total):
        is_warmup = i < args.warmup
        tag = "warmup" if is_warmup else f"run {i - args.warmup + 1}/{args.runs}"
        try:
            result = single_run(args, binary, env_overrides, i - args.warmup)
        except Exception as exc:
            print(f"  {tag}: FAILED: {exc}")
            continue

        fp = result["t"].get("firstPaint")
        uss = dig(result, "settled.mem.residentUnique")
        mods = dig(result, "settled.esModuleCount")
        print(
            f"  {tag}: firstPaint {fp}ms, "
            f"USS {uss / 1e6 if uss else 0:.1f}MB, {mods} ES modules"
        )
        if not is_warmup:
            modules["esModules"] = result.pop("_esModules")
            modules["jsModules"] = result.pop("_jsModules")
            runs.append(result)
        else:
            result.pop("_esModules", None)
            result.pop("_jsModules", None)

    if not runs:
        sys.exit("no successful runs")

    payload = {
        "label": args.label,
        "binary": str(binary),
        "env": env_overrides,
        "prefs": args.pref,
        "home": args.home,
        "headless": args.headless,
        "settle": args.settle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runs": runs,
        "modules": modules,
    }
    out = RESULTS / f"{args.label}.json"
    out.write_text(json.dumps(payload, indent=1))
    print(f"\nwrote {out.relative_to(HERE.parent)} ({len(runs)} runs)")
    print()
    report_single(payload)


def series(payload, key):
    values = [dig(run, key) for run in payload["runs"]]
    return [v for v in values if isinstance(v, (int, float))]


def fmt(value, unit):
    if value is None:
        return "-"
    if unit == "bytes":
        return f"{value / 1e6:.1f}MB"
    if unit == "ms":
        return f"{value:.0f}ms"
    return f"{value:.0f}"


def report_single(payload):
    print(f"{'metric':<28} {'median':>12} {'min':>12} {'spread':>10}")
    print("-" * 66)
    for key, label, unit in METRICS:
        values = series(payload, key)
        if not values:
            continue
        med = statistics.median(values)
        spread = (max(values) - min(values)) if len(values) > 1 else 0
        pct = f"{100 * spread / med:.1f}%" if med else "-"
        print(
            f"{label:<28} {fmt(med, unit):>12} {fmt(min(values), unit):>12} {pct:>10}"
        )


def load(label):
    path = RESULTS / f"{label}.json"
    if not path.exists():
        sys.exit(f"no results for {label!r} (expected {path})")
    return json.loads(path.read_text())


def module_group(uri):
    """Coarse bucket for an ESM URI, for grouping the diff readably."""
    tail = uri.split("://", 1)[-1]
    parts = [p for p in tail.split("/") if p]
    if len(parts) <= 1:
        return tail
    return "/".join(parts[:-1])


def cmd_compare(args):
    base = load(args.base)
    variant = load(args.variant)

    print(f"base    : {base['label']}  env={base['env'] or '(none)'}")
    print(f"variant : {variant['label']}  env={variant['env'] or '(none)'}")
    print()

    header = f"{'metric':<28} {'base':>11} {'variant':>11} {'delta':>11} {'':>8}"
    print(header)
    print("-" * len(header))
    for key, label, unit in METRICS:
        base_values = series(base, key)
        var_values = series(variant, key)
        if not base_values or not var_values:
            continue
        base_med = statistics.median(base_values)
        var_med = statistics.median(var_values)
        delta = var_med - base_med
        pct = f"{100 * delta / base_med:+.1f}%" if base_med else "-"
        noise = max(
            (max(base_values) - min(base_values)) if len(base_values) > 1 else 0,
            (max(var_values) - min(var_values)) if len(var_values) > 1 else 0,
        )
        flag = "*" if abs(delta) > noise >= 0 else " "
        sign = "+" if delta > 0 else ""
        shown = f"{sign}{fmt(delta, unit)}" if unit != "ms" else f"{delta:+.0f}ms"
        print(
            f"{label:<28} {fmt(base_med, unit):>11} {fmt(var_med, unit):>11} "
            f"{shown:>11} {pct:>7}{flag}"
        )
    print("\n* = |delta| exceeds observed run-to-run spread")

    for kind in ("esModules", "jsModules"):
        base_set = set(base["modules"].get(kind) or [])
        var_set = set(variant["modules"].get(kind) or [])
        avoided = base_set - var_set
        added = var_set - base_set
        if not avoided and not added:
            continue
        print(f"\n=== {kind}: {len(avoided)} avoided, {len(added)} newly loaded ===")
        if avoided:
            groups = {}
            for uri in avoided:
                groups.setdefault(module_group(uri), []).append(uri)
            for group, uris in sorted(groups.items(), key=lambda kv: -len(kv[1])):
                print(f"  -{len(uris):<4} {group}")
                if args.verbose:
                    for uri in sorted(uris):
                        print(f"          {uri.rsplit('/', 1)[-1]}")
        if added:
            print("  newly loaded (unexpected -- check for regressions):")
            for uri in sorted(added):
                print(f"    + {uri}")


def cmd_report(args):
    payload = load(args.label)
    print(f"{payload['label']}  env={payload['env'] or '(none)'}")
    print(f"{len(payload['runs'])} runs, {payload['timestamp']}")
    print()
    report_single(payload)
    if args.modules:
        groups = {}
        for uri in payload["modules"].get("esModules") or []:
            groups.setdefault(module_group(uri), 0)
            groups[module_group(uri)] += 1
        print(f"\n=== ES modules by directory ({sum(groups.values())} total) ===")
        for group, count in sorted(groups.items(), key=lambda kv: -kv[1])[: args.top]:
            print(f"  {count:<5} {group}")


def load_memory_report(label):
    """Sum nsIMemoryInfoDumper 'explicit/...' amounts per path, per process."""
    import gzip

    path = MEMREPORTS / f"{label}-memory.json.gz"
    if not path.exists():
        sys.exit(f"no memory report for {label!r}; re-run with --memory-report")
    with gzip.open(path, "rt") as fh:
        data = json.load(fh)

    totals = {}
    for report in data.get("reports", []):
        if report.get("units") != 0:  # 0 == BYTES
            continue
        process = report.get("process") or "(parent)"
        # Keep the process kind, not the pid, so labels line up across runs.
        kind = "parent" if "Main Process" in process or not process else "child"
        key = (kind, report.get("path", ""))
        totals[key] = totals.get(key, 0) + (report.get("amount") or 0)
    return totals


def roll_up(totals, depth):
    """Collapse 'explicit/js-non-window/zones/...' to the first `depth` segments."""
    rolled = {}
    for (kind, path), amount in totals.items():
        if not path.startswith("explicit/"):
            continue
        parts = path.split("/")
        key = (kind, "/".join(parts[:depth]))
        rolled[key] = rolled.get(key, 0) + amount
    return rolled


def cmd_memdiff(args):
    base = load_memory_report(args.base)
    variant = load_memory_report(args.variant)

    base_r = roll_up(base, args.depth)
    var_r = roll_up(variant, args.depth)

    rows = []
    for key in set(base_r) | set(var_r):
        b, v = base_r.get(key, 0), var_r.get(key, 0)
        if abs(v - b) >= args.threshold:
            rows.append((v - b, key, b, v))
    rows.sort(key=lambda r: r[0])

    base_total = sum(v for k, v in base_r.items() if k[0] == "parent")
    var_total = sum(v for k, v in var_r.items() if k[0] == "parent")
    print(
        f"parent explicit: {base_total / 1e6:.1f}MB -> {var_total / 1e6:.1f}MB "
        f"({(var_total - base_total) / 1e6:+.1f}MB)"
    )
    print(
        f"\nmovers >= {args.threshold / 1e3:.0f}KB, rolled up to depth {args.depth}\n"
    )
    print(f"{'delta':>10} {'base':>10} {'variant':>10}  path")
    print("-" * 78)
    for delta, (kind, path), b, v in rows:
        tag = "" if kind == "parent" else " [child]"
        print(f"{delta / 1e3:>9.0f}K {b / 1e3:>9.0f}K {v / 1e3:>9.0f}K  {path}{tag}")
    if not rows:
        print("(no movers above threshold)")


def cmd_categories(args):
    """Show the startup category registrations, i.e. the SLIM_UI gate surface."""
    payload = load(args.label)
    cats = None
    for run in payload["runs"]:
        cats = dig(run, "settled.categories") or dig(run, "early.categories")
        if cats:
            break
    if not cats:
        sys.exit(f"no category data in {args.label!r}; re-run to collect it")

    total = 0
    for name, entries in cats.items():
        if not entries:
            continue
        print(f"\n=== {name} ({len(entries)}) ===")
        for entry in entries:
            module, _, value = entry.partition("|")
            total += 1
            print(f"  {value:<52} {module}")
    print(
        f"\n{total} registrations across {len([c for c in cats.values() if c])} categories"
    )


def cmd_profile(args):
    """One instrumented run producing a Firefox Profiler JSON."""
    binary = find_binary()
    args.profile_template = resolve_profile_template(args, binary)
    out = Path(args.output or (RESULTS / f"{args.label}-startup-profile.json"))
    out.parent.mkdir(parents=True, exist_ok=True)

    env_overrides = {
        "MOZ_PROFILER_STARTUP": "1",
        "MOZ_PROFILER_STARTUP_NO_BASE": "1",
        "MOZ_PROFILER_STARTUP_INTERVAL": str(args.interval),
        "MOZ_PROFILER_STARTUP_ENTRIES": str(args.entries),
        "MOZ_PROFILER_STARTUP_FEATURES": args.features,
        "MOZ_PROFILER_STARTUP_FILTERS": args.filters,
        "MOZ_PROFILER_SHUTDOWN": str(out),
    }
    for item in args.env:
        key, _, value = item.partition("=")
        env_overrides[key] = value or "1"

    print(f"profiling into {out}")
    single_run(args, binary, env_overrides, 0)
    if out.exists():
        print(f"wrote {out} ({out.stat().st_size / 1e6:.1f}MB)")
        print("open at https://profiler.firefox.com/ (Load a profile from file)")
    else:
        print("WARNING: no profile written; check MOZ_PROFILER_* support in this build")


def add_run_args(parser):
    parser.add_argument("--runs", type=int, default=8)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--settle",
        type=float,
        default=5.0,
        help="seconds to wait before the second snapshot, to catch idle tasks",
    )
    parser.add_argument("--home", default="about:blank")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--gecko-log", action="store_true")
    parser.add_argument(
        "--keep-cache",
        dest="purge_cache",
        action="store_false",
        help="keep the cloned profile's JS startup cache. Only safe when the "
        "binary has not been rebuilt since the template profile was warmed",
    )
    parser.add_argument(
        "--memory-report",
        action="store_true",
        help="dump a full about:memory report on the first measured run",
    )
    parser.add_argument(
        "--profile-template",
        default=None,
        help="warmed profile to clone per run (default: the MCP profile in objdir/tmp)",
    )
    parser.add_argument(
        "--no-mcp-prefs",
        dest="mcp_prefs",
        action="store_false",
        help="omit the prefs mach firefox-devtools-mcp launches with",
    )
    parser.add_argument(
        "--pref-baseline",
        default="geckodriver",
        choices=["geckodriver", "marionette", "minimal"],
        help="starting pref state. 'geckodriver' matches what mach "
        "firefox-devtools-mcp actually gets (default); 'marionette' keeps the "
        "Python client's much larger forced set, which pre-disables a lot",
    )
    parser.add_argument("--env", action="append", default=[], metavar="K=V")
    parser.add_argument("--pref", action="append", default=[], metavar="k=v")
    parser.add_argument(
        "--pref-set",
        action="append",
        default=[],
        metavar="NAME",
        help="apply perf-lab/presets/NAME.json (repeatable, later wins)",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="benchmark a variant")
    run.add_argument("--label", required=True)
    add_run_args(run)
    run.set_defaults(func=cmd_run)

    compare = sub.add_parser("compare", help="diff two labelled results")
    compare.add_argument("base")
    compare.add_argument("variant")
    compare.add_argument("-v", "--verbose", action="store_true")
    compare.set_defaults(func=cmd_compare)

    memdiff = sub.add_parser("memdiff", help="diff two about:memory reports")
    memdiff.add_argument("base")
    memdiff.add_argument("variant")
    memdiff.add_argument("--depth", type=int, default=3)
    memdiff.add_argument("--threshold", type=float, default=100_000)
    memdiff.set_defaults(func=cmd_memdiff)

    cats = sub.add_parser("categories", help="list startup category registrations")
    cats.add_argument("label")
    cats.set_defaults(func=cmd_categories)

    report = sub.add_parser("report", help="re-print one result")
    report.add_argument("label")
    report.add_argument("--modules", action="store_true")
    report.add_argument("--top", type=int, default=40)
    report.set_defaults(func=cmd_report)

    prof = sub.add_parser("profile", help="capture a startup Gecko profile")
    prof.add_argument("--label", default="baseline")
    prof.add_argument("--output")
    prof.add_argument("--interval", type=float, default=1)
    prof.add_argument("--entries", type=int, default=100000000)
    prof.add_argument(
        "--features", default="js,stackwalk,cpu,processcpu,ipcmessages,memory"
    )
    prof.add_argument("--filters", default="GeckoMain,Compositor,Renderer,DOM Worker")
    add_run_args(prof)
    prof.set_defaults(func=cmd_profile)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
