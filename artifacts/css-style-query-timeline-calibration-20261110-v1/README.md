# Animated style-query invalidation

The color-only reduction reproduces an animation-driven style-query invalidation
failure in both the local branch browser and installed Nightly 162.0a1,
BuildID 20261109214446. Named and unnamed animated cases fail; both ordinary
custom-property controls pass. The source reaches `--gate: on` at paused CSS
animation progress 0.75, but the dependent color remains black through repeated
reads and two animation frames. A target class mutation that requests matching
changes it to the required green. Local and installed observations are identical.

The first four-case timeline probe found this failure before reaching its
animated timeline-source assertions. Ordinary name and scope controls pass all
three on/off/on source switches. This does not demonstrate a separate stale
timeline registry: in animated cases the literal query rule itself did not match.
No direct animated `var()` substitution occurs in these timeline declarations.

| Run | Animated cases | Ordinary controls | Harness |
| --- | --- | --- | --- |
| Local timeline probe | 2 FAIL at query matching | 2 PASS | OK |
| Local color reduction | 2 FAIL | 2 PASS | OK |
| Installed Nightly color reduction | 2 FAIL | 2 PASS | OK |

`ROOT-COMPARISON.json` authenticates exact raw statuses and observation records.
Each color callback records all temporal observations before its assertions;
its forced-matching control passes before the expected first-read assertion fails.
Later color assertions are not counted as passing assertions, although their
values are explicitly observed. The ordinary controls and forced-rematch result
establish that the tested query syntax is supported.

## Contract and source hypothesis

The pinned primary Conditional Rules Level 5 sections require style queries to
use computed values and query evaluation changes caused by animation effects to
participate in style change events. This is a human-reviewed expectation, not a
formal derivation of the browser result. Primary snapshots are style-container.md
and animated-containers.md, including their document hash.

The local Git-pinned data.rs and matching.rs show that custom-property changes
produce named/unnamed style-query hints, while animation-only traversal cannot
perform selector matching. The separate handoff review traces where normal work
is lost and prepares a query-only candidate. The existing held font/drain repair
has not been changed or validated by these runs. This lead is distinct from the
animation-taint substitution lead, but no novelty against all upstream reports is
claimed. No native repair has yet been delivered for this issue.

## Reproduction and environment

`run.py runtime1` ran the timeline fixture. `run_color.py color1` and
`run_color_installed.py installed-color1` ran the same reduced fixture against
the local and installed browsers respectively. Output directories must be new.
Each script requires `python3 -I` and uses the existing local Mach environment.
No compilation occurred. Explicit prefs enable style queries and scroll-driven
animations and disable CSS display animations. Release-channel exposure is not
established by these feature-enabled Nightly runs.

`check_wpt.py check2` and `check_color.py color-check` validate syntax, inert
callback registration, genuine WPT lint and one-page manifests. check1 is earlier
preparation before recording the explicit style-query pref. The two HTML files
remain research artifacts; temporary WPT installations were removed.

Independent restoration checks passed after all three runs: full local app,
three build extras, unchanged Git HEAD/index, baseline binary hashes, terminal
owned process groups and removed backups. The installed executable, XUL and
application metadata hashes also match before and after. Receipts bind historical
checkpoint d82e1bf0282e; rerunning their Git audit after later commits would reject
the changed history. Active objdir retained; all three temporary app backups removed.
