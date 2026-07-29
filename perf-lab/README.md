# perf-lab: SLIM_UI startup measurement loop

Measures Firefox startup time and memory for the `mach firefox-devtools-mcp` launch
path, so changes that strip human-only UI/services can be evaluated.

Untracked scratch tooling, not intended to land as-is.

## Usage

```sh
# baseline (what the MCP gets today)
./mach python perf-lab/startup_bench.py run --label mcp-baseline --runs 5

# a variant
./mach python perf-lab/startup_bench.py run --label try-newtab-off \
    --runs 5 --pref-set off-newtab

# the category gate
./mach build faster && \
./mach python perf-lab/startup_bench.py run --label slim --runs 5 \
    --pref-set slim --pref browser.newtab.preload=false

./mach python perf-lab/startup_bench.py compare mcp-baseline try-newtab-off
./mach python perf-lab/startup_bench.py report mcp-baseline --modules

# attribution: full Gecko profile, load at https://profiler.firefox.com/
./mach python perf-lab/startup_bench.py profile --label baseline
```

`--pref-set` reads `presets/<name>.json` and is repeatable (later wins), so
subsystems can be measured individually and then composed.

## What it does

Launches Firefox via the Marionette Python client, then from chrome context reads
`Services.startup.getStartupInfo()`, `nsIMemoryReporterManager`,
`Cu.loadedESModules`, and `ChromeUtils.requestProcInfo()`. Two snapshots per run:
one at session start, one after `--settle` seconds (default 5) to capture the
`_scheduleStartupIdleTasks` work, which is where most of BrowserGlue's cost lives.

Fidelity notes, both of which bit during development:

- The Marionette Python client normally forces ~120 prefs of its own and sets
  `remote.prefs.recommended=false`. That is *not* what the MCP gets — it launches
  through geckodriver, whose set is much smaller. `--pref-baseline geckodriver`
  (default) replaces the client's dicts with geckodriver's, keeping only what
  Marionette needs to stay usable. With the client's own prefs, ~47 modules of
  startup work are invisible.
- Runs clone the MCP's persistent profile (`objdir/tmp/profile-default`) rather
  than starting fresh, so one-time first-run costs don't dominate. Use
  `--profile-template none` for a cold profile.

## The startup-cache trap (read this before trusting a result)

`./mach build faster` does **not** bump the BuildID. Gecko therefore treats a
cloned profile's `scriptCache.bin` as valid and runs the *previous* build's
bytecode, so a frontend change measures as a perfect no-op. This cost real time
during development: the first SLIM_UI run reported byte-identical module counts.

Runs now delete `startupCache/` from each cloned profile by default. Both sides of
a comparison pay the same rebuild cost, so deltas stay valid; absolute startup
times are inflated relative to a cache-warm launch. `--keep-cache` opts out, and
is only safe if the binary has not been rebuilt since the template was warmed.

The guard against this class of mistake is `slimUIReport.unmatched` — skip entries
that matched nothing are reported, so a stale or typo'd name surfaces instead of
quietly measuring as "no win".

## Reading the output

**Lead with the module-list diff and memory, not the timings.** Timing spread is
6-16% run-to-run on this machine, so a sub-50ms delta at `--runs 5` is noise. The
`compare` output flags with `*` any delta exceeding observed spread. Module counts
are near-deterministic (0.2-1% spread) and are the fastest honest signal for
"did this change actually avoid loading the code".

Caveat on module counts: `Cu.loadedESModules` only sees ES modules. 20 of the 94
category registrations live in `chrome://browser/content/*.js` subscripts, which
are invisible to it — sparing `PanelUI.init`, `SidebarController.init` and
`gUnifiedExtensions.init` moved the count by exactly 0. Use `memdiff` and the
`slimUIReport.skipped` list to judge those.

## Known caveats

- The GPU process fails to launch in this artifact build (`posix_spawnp Error:2`),
  so it falls back to software WebRender. Consistent across variants, so deltas
  hold, but absolute numbers are not production-representative.
- Artifact builds cannot measure C++ changes. Use `MOZCONFIG=mozconfig-full` for
  those. Frontend-only changes need `./mach build faster` to repack omni.ja.
- Marionette itself adds startup cost. Constant across variants.

## The gate

`toolkit/modules/BrowserUtils.sys.mjs` filters `callModulesFromCategory` against a
skip list when the pref is on. That one hook covers all 94 startup registrations
across the 13 `browser-*` categories, rather than editing dozens of call sites.

Two prefs, declared in `browser/app/profile/firefox.js`:

- `browser.slimui.enabled` (bool, default false) — the switch, read once at startup
- `browser.slimui.skip` (string, default "") — override the built-in list

Prefs rather than an env var so the same switch works everywhere a pref can be
set: `.mcp.json --pref`, `./mach run --setpref`, geckodriver capabilities,
`testing/profiles` in CI.

```sh
# spare three entries from the built-in list (bisection)
--pref 'browser.slimui.skip=-PanelUI.init,-SidebarController.init'
# or replace it wholesale
--pref 'browser.slimui.skip=AboutNewTab.init,Normandy.init'
```

To drive the real MCP with it, add to the `firefox-devtools` args in `.mcp.json`:

```json
"--pref", "browser.slimui.enabled=true"
```

`./mach python perf-lab/startup_bench.py categories <label>` dumps the live
registration list, which is where the skip list came from (guessing the names
would have silently no-opped).

## Baseline as of 2026-07-25

`about:blank`, artifact build, 5 runs: firstPaint2 714ms, 621 ES modules,
292MB parent USS, 606MB across 9 processes.

Enabling `remote.prefs.recommended` (the one pref the MCP explicitly disables)
buys -47 modules / -8MB USS / -28ms firstPaint2, i.e. ~4%. Two thirds of that is
newtab/activity-stream.

The category gate does much better. With `browser.slimui.enabled` plus
`browser.newtab.preload=false`, 72 of 73 entries matched and no modules were
newly loaded:

| | base | SLIM_UI | delta |
|---|---|---|---|
| ES modules | 621 | 420 | **-201 (-32%)** |
| parent USS | 311MB | 206MB | **-105MB (-34%)** |
| parent heap | 279MB | 202MB | -77MB (-28%) |
| RSS all procs | 650MB | 498MB | -152MB (-23%) |
| parent `explicit` | 293MB | 194MB | -100MB |

Attribution (`memdiff`): JS runtime -26MB, JS zones -22MB, gfx/webrender -17MB,
SQLite -16MB, preloaded about:newtab child -12MB, chrome worker -4.6MB,
startup cache -4.3MB, network cache -4.2MB.

**Timings are not yet credible** — every run so far was taken with a full build
competing for CPU, and the numbers disagree between runs (-308ms then +68ms
firstPaint2). Needs a re-run on an idle machine before any timing claim.

## Not yet done

- Per-entry attribution: which of the 72 carry the win is unmeasured.
- Broader QA. The pass above covered navigate, snapshot, click, fill, select,
  history, tabs, screenshot, console, network. Not covered: dialogs, file upload,
  downloads, DevTools toolbox, extension install, private browsing.
- Nothing runs in CI. A mochitest asserting `slimUIReport.unmatched` is empty
  would catch skip entries going stale as the manifests change.
