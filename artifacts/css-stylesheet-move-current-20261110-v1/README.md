# Preserve CSSOM state during stylesheet-owner moves

A state-preserving `moveBefore()` currently passes stylesheet owners through ordinary removal and insertion handling. That clears their associated stylesheet and recreates it from source text or cached resource contents. CSSOM edits and the original object association are lost even though the owner remains connected.

The repair passes the existing move flag through the HTML style/link and SVG style bind/unbind paths. During a move it removes a completed sheet from the old collection and reinserts that same sheet at its new tree position. It retains the owner association, rule list and disabled state. Ordinary removal still uses the existing update path. Pending loads continue with the current owner; no new sheet ownership or raw-pointer lifetime mechanism is introduced.

## Normative and source review

The refreshed DOM move algorithm invokes moving steps rather than insertion/removing steps; its root checks permit document/shadow-root moves within the same shadow-including root. HTML's style update triggers and the CSSOM associated-sheet getter supply the remaining association argument, as recorded in the retained `historical-spec-trace.md`. The identity conclusion is an interpretation of that algorithm chain, not a single literal assertion in the specification. `spec-move.json` retains the current query and content hash.

Source review checked completed/disabled sheets, direct and ordinary-ancestor moves, pending-link completion, old/new collection membership, ordinary removal, SVG style and the existing SVG-use exclusion. Context headers are included directly in every newly dereferencing translation unit. The native candidate is byte-identical to the earlier include-corrected candidate; no source rebase was required on this branch.

The delivery contains five native files, three WPT pages and four CSS resources. The lifecycle selection omits three moved-shadow-host registrations that depend on local repair #148. The retained 29 authored callbacks plus two existing controls are executed as exact files here; earlier full-suite/body-correspondence evidence is not substituted for this run. Direct cross-root cases, stationary controls, ordinary reinsertion, CSSOM mutation through retained handles, disabled toggles, pending links, cascade order, implicit scope and no-refetch behavior are covered. This does not claim complete DOM move or native-memory verification.

## Current native evidence

Before installation, all five source preimages matched the saved candidate's base, and the baseline browser hashes matched the completed shared-media build. The selected five pages produced 14 PASS / 17 FAIL with five OK endings. Installed Nightly reproduced the identical callback statuses, with its binary hashes unchanged across the run. These failures are manifestations of one stylesheet-state repair, not 17 separately counted bugs.

The candidate compiled with `mach build binaries -j6` in the existing object directory. C++ formatting and WPT lint passed. As in the preceding build, Mach logged a progress reporter `KeyError: export` while the native build completed successfully. `build-result.json` pins the source, selected tests and installed binary hashes; the native source was uncommitted during compilation.

The exact selected candidate completed 31 PASS with five OK endings, preserving all 14 previous passing callback signatures and improving all 17 target failures. Source, test and binary hashes still matched the build record after execution. This closes the earlier exact-filtered-file execution gap.

The preceding shared-media repair was rechecked in this combined build: both regression pages retained all eight passes and two OK endings. This checks the interaction between the two stylesheet-collection repairs.

## Upstream applicability

The original native patch applied to four pinned upstream files but two context hunks failed in `HTMLLinkElement.cpp`. That initial failure is retained in `upstream-result.json` and `upstream-apply.log`. A separate context adaptation preserves exactly the same added and removed lines, uses unique exact replacements in that file, and leaves all other upstream text intact. The adapted patch applies and reverses with zero fuzz and exact byte recovery at revision `47f2a88cbab9072c8f8f156494b92d6891e488fb`; see `upstream-adapted-result.json` and `upstream-context-adapted.patch`. No isolated upstream build or runtime validation is claimed, and the original patch is not described as directly cherry-pickable there.

## Saved-evidence check and publication

Run `python3 -I -B check.py`. It checks file digests, exact callback identities, all prior passes, all target improvements and harness endings. It does not execute Firefox or prove a source-to-binary correspondence. `COMMANDS.json` records the actual invocation arguments; logs and raw WPT events retain observations.

The historical publisher remains unchanged because its fixed-ancestor admission no longer applies. This continuation uses current source hashes, explicit twelve-path staging, and signed local research before the production repair. No external submission or Try push is included.
