# Pseudo-element follow-up

Six ready-phase rows: **three discrepancies, three passing no-op controls**. All initial and full-sheet-refresh calibrations pass; runtime source, binary, runner and test pins remain stable.

Add, Delete and Clear leave stale root `::before`, descendant `::before`, and `::view-transition-group(root)` opacity, alongside ordinary root color and descendant width. No-op Add-existing, Delete-absent and Clear-empty pass. The values are respectively .2/.8, .25/.75 and .3/.7 for absent/present alpha. Direct selector membership and active owner identity remain correct. A full stylesheet disable/flush/re-enable repairs all values.

The group animation remains `-ua-view-transition-group-anim-root` with computed duration 100s. Raw animation records show it running on `::view-transition-group(root)` and distinguish the old/new fade animations. Complete retained `BuildGroupKeyframes` creates only transform, width, height and backdrop-filter entries at its two endpoints; it does not animate group opacity. The fixture supplies no additional group animation. Thus the sampled opacity is a deterministic ordinary declaration observer, not an uncertain cross-fade progress measurement. This combines raw runtime controls and source inspection, not a universal animation proof.

The source and normative interpretation are those in the frozen `css-view-transition-type-invalidation-v1` report. This follow-up is an additional local baseline on the same existing shared Firefox 160 development binary, not an isolated repair or release-browser experiment. It does not alter that frozen artifact or its final 18-case WPT proposal. Root owns any landing-test extension and native repair.

Fresh owned browser process terminated and profile removed; user.js, raw results, logs, source and binary pins retained. No native, live WPT, Git, or build changes.
