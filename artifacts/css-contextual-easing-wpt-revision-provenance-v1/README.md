# WPT revision provenance correction

The first contextual-easing baseline incorrectly equated raw `run_info.revision` with the browser application's build revision. `RunInfo.__init__` obtains that field from `GitTree.rev`, which runs `git rev-parse HEAD` in the harness checkout. Firefox's separate `run_info_browser_version` obtains `browser_build_id` and `browser_changeset` from `mozversion` for the selected binary.

The saved original run reports workspace revision `4f4bfa099bb141f29c70698b9d6a1fc87efbc1b2`, BuildID `20261028160524`, and null `browser_changeset`; its authenticated application metadata records build revision `bbef4930ab65261f7aa539c4f46ccc84f3968bbb`. These are distinct sources of provenance, not contradictory browser versions.

The corrected adapter binds raw revision to the frozen harness HEAD and raw BuildID to independently captured application metadata. That metadata's revision remains bound to the actual saved build/source lineage. Null `browser_changeset` supplies no additional revision claim. Stable cross-phase run-info comparison retains the harness revision and permits only the independently checked BuildID to change.

The first run also exposed sixteen null-body fixture exceptions. Its raw records and rejected assessment remain unchanged. Adding an explicit body before both inline test scripts and conducting a fresh baseline addresses that separate setup defect; this record does not reinterpret those sixteen failures as feature evidence. No native fix, browser execution, acceptance or formal coverage is claimed here.
