# CSSOM rectangle four-variant experiment

Status: diagnostic comparison complete; standalone fix acceptance remains separate.

| Actual build | New WPT PASS | New WPT FAIL | Existing subtests | Existing reftest |
| --- | ---: | ---: | --- | --- |
| Baseline | 12 | 16 | 27 PASS, 2 expected FAIL | PASS |
| DOMRect double setters only | 20 | 8 | 27 PASS, 2 expected FAIL | PASS |
| Integer translation only | 16 | 12 | 27 PASS, 2 expected FAIL | PASS |
| Both | 28 | 0 | 27 PASS, 2 expected FAIL | PASS |

Every run completed all 14 files and 57 unique subtests, with 13 OK harnesses and
one passing reftest. No baseline PASS changed to failure. The two existing
failures concern rotated SVG text/Range bounds and trailing surrogate indexing;
they remain expected failures. Their complete status and message records are
retained, including precision changes to messages. This is not a claim that all
existing assertions passed.

The corrected proposed roster is 24 parameter combinations plus four coordinate
effects, not the producer's superseded 52 count. Small cases and transform,
scroll and zoom controls pass throughout. DOMRect-only fixes all eight exponent
boundary combinations; integer-only fixes four large/integer-host combinations.
Fractional-host integration cases can require both corrections. The standalone
identity-transform witness is not part of this run and needs its own execution.

Removing DOMRect narrowing exposes the still-unfixed graphics loss more directly:
the large integer-host edge changes from 100.015625 to 100.01666259765625 rather
than becoming 100. This remains a failure. The comparison establishes no new
failing status, not a universal reduction in distance from the CSS edge.

All four builds also completed the same 56-row observer probe, with stable
source/binary pins and removed private profiles. Eight non-flex rows include
both axes and padding variants. In the four large rows, baseline edges are
100.015625, DOMRect-only edges are 100.01666259765625, and integer-only/both
edges are 100; descendant markers remain 100. The 48 flex/replaced/table records
are retained as diagnostic observations. No obsolete table inner-box oracle is
silently reclassified as a passing caption-inclusive bounding rectangle.

The baseline binary was authenticated against the preceding restored build.
All three candidate builds and the final restore build exit 0. Source snapshots
show each actual variant changes exactly its designated implementation file(s).
The known Mach logging KeyError for the export tier is retained in build logs;
it did not prevent successful compiler/linker completion. These are shared
project builds with the preexisting local research changes pinned in each run,
not isolated upstream or all-platform builds.

The two source files and temporary WPT are restored; HEAD and index are unchanged.
RESTORED.json pins the final baseline binary and source set. No candidate is
installed or counted as an accepted fix by this artifact.

Root authenticated the 175-payload proposal and freshly replayed its 19 helper
checks and six semantic mutants at O0/O2 with UBSan. The first replay attempt
failed before compilation because its output parent did not exist; the corrected
setup and successful replay are retained. This finite extracted execution uses
frame/provider facades, not the complete Gecko transform traversal. Actual
frame/matrix correspondence, universal IEEE mapping and full safe-origin F1–F12
remain separate obligations.

Source basis: [CSSOM View rectangle algorithms](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects)
and [Geometry DOMRect](https://drafts.csswg.org/geometry/#DOMRectReadOnly), checked
20 October 2026. The test compares aligned edges; it does not loosen the original
exact-origin contract to a large tolerance.
