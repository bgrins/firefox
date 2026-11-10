# Bug 2085413 WPT delivery

Prepared final file: `animated-custom-property-style-queries.html` (102 lines), for `testing/web-platform/tests/css/css-conditional/container-queries/`. SHA-256: `d8eced0712ae27f9fd50deced397feb7ef39113b94ea7fe6b73bf9aa2654bc51`.

One coherent testharness file registers 13 callbacks. All cases use on/off/on. Each captures the first descendant color reads before checking the source value; animated cases additionally verify their CSS animation identity, computed progress, and paused state. The decisive assertion therefore cannot be repaired by an earlier source getter. Debug dumps, forced rematches, and later-frame observations were removed.

| Cases | Purpose |
| --- | --- |
| named, unnamed | Minimal animation-driven style-query invalidation |
| ordinary-named, ordinary-unnamed | Ordinary property-change controls |
| deep | 256 nested wrappers; bounded ancestry replay coverage, not a timing benchmark |
| siblings | Eight affected children |
| pseudo | `::before` query target |
| hidden | Computed style under `display:none` |
| nearest-named | Nearer named container with an explicit overriding custom property remains authoritative |
| registered | Registered `<custom-ident>`, `inherits:false`, named query across intermediates |
| two-producers | Two sibling animated containers, each with its own target, toggled before the shared first flush |
| nearest-unnamed | Nearest unnamed container's explicit override remains authoritative |
| reveal | Hidden subtree revealed at the first animated on sample, then off/on updates after visibility is restored |

`check1/ROSTER.json` lists exact callback names. `python3 -I check_wpt.py check2` reproduces syntax, inert callback registration, genuine WPT lint, and one-page manifest generation in a fresh temporary staging directory. Use a new output-directory name. `check1` completed successfully with 13 callbacks and no lint findings; temporary staging was removed. These checks do not execute assertions or claim a browser pass. Only `layout.css.style-queries.enabled=true` is recorded as a Firefox test preference; this file has no timeline dependency.

`PROVENANCE.json` authenticates the two original fixtures, inherited static-checker input, and native candidate patch/role manifest. Their exact copies are retained in `inputs/`. The native candidate is based on `d82e1bf0282ecb524b016cedfbba4f6d4188d449`; this delivery changes no native file. The final fixture is a manual consolidation with three new cases and needs the requested exact-file candidate run with `STYLO_THREADS=4` before committing. No live WPT installation, Git mutation, build, or browser execution occurred in this capsule.

Suggested commit subject:

`Bug 2085413 - Restyle style-query dependents after custom-property animations.`

Keep the native repair and this single WPT together. Research and validation artifacts belong in the preceding research commit. The repair addresses an existing public bug; it does not establish global animation-drain convergence or release held #160.
