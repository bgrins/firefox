# Font sampling diagnostic terminal review

Independent raw-result/full-restoration audit passes; runtime hold released. Three callbacks PASS, one harness OK, fifteen unique phase-ordered records. Lint/WPT exit 0, wrapper exits 0, no native build. Frozen manifest 1b32949c6fec8b10df3781d2ef4ee41561a203b1f10d941d019254f1f21f7aee; HEAD ec467c0219d3d5daf70f42fcc53677cf8a262173.

| Scenario | Sync seek / ready / reseek | Unrelated color invalidation / subsequent two frames |
| --- | --- | --- |
| CSS font + relative margin | font 10px, margin 16px | font 15px, margin 22.5px |
| CSS font only | font 15px, margin 0px | unchanged |
| WAAPI font + relative margin | font 15px, margin 22.5px | unchanged |

Before/after style reads agree in every record. All before/after timing states agree: current/local time 50000, progress .5, paused, pending false, rate 1, null start, iteration 0 and duration/activeDuration/endTime 100000. Ready observer has run after the ready stage. Reseek genuinely sets 25000 then 50000. The CSS font+margin values remain stale through those stages, despite correct reported timing; changing only color causes the expected font/margin pair. The two controls discriminate the combined CSS-dependent-property path from a general font interpolation or WAAPI failure.

Getter frames still retain specified 1em/2em margins, independently of style repair, consistent with the separately reproduced getter issue. CSS frame offsets are explicit 0/1; WAAPI offsets remain null with computed 0/1. This diagnostic does not change their oracle or establish a native root cause.

The first synchronous font read exactly precedes ready/state access. CSSAnimation GetReady, PlayStateFromJS and PendingFromJS can flush unanimated style, and stateBefore uses these accessors before getKeyframes. Therefore the observations are sequential with observer effects, not atomic snapshots. Here none of those reads repairs the CSS combination; ready/reseek also do not. The two frame waits occur only AFTER explicit style invalidation, so the experiment cannot say whether frame waits alone would repair or preserve the stale state. No attribution to held159/160 follows; compare source/evidence separately before a duplicate or new-bug classification.

Independent verification reconstructed raw callback lifecycle/inventory and all observation IDs/fields, then replayed the frozen full-schema parser and matched saved records. Full app scan covers 9,378 entries and three extras; retained source/test/binary/configuration pins, profile/test absence, HEAD/logical index and clean tracked state match. Owned groups, fixture/metadata, backups and lock are absent. Familiar nonfatal SWGL framebuffer/Nimbus logs remain; no harness crash/timeout/loss occurred.

Root ran the diagnostic. Reviewer authored its proposal/wrapper and independently validates execution/restoration, not wrapper authorship. No native repair, catalogue increment, general sampling proof or final missing-pseudo/debug acceptance is claimed.
