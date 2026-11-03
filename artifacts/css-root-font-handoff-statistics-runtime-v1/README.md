# Root font handoff traversal counts

Existing DUMP_STYLE_STATISTICS output was captured around one already-prepared root-animation seek and the first child font-size getter. Both archived candidates returned64px, with initial root16/child32, paused effects and5000fixed13px leaves calibrated before the action. Cleanup after the captured interval confirmed root32/child64 and unchanged leaves/effect times.

| Captured traversal | Broad traversed / styled / reused | Selective traversed / styled / reused |
| --- | --- | --- |
| 1 | 3 / 3 / 0 | 3 / 3 / 0 |
| 2 | 5005 / 5004 / 4994 | 5005 / 1 / 0 |
| 3 | 3 / 1 / 0 | 3 / 1 / 0 |
| 4 | 5005 / 5004 / 4994 | 5005 / 1 / 0 |
| Total | 10016 / 10012 / 9988 | 10016 / 6 / 0 |

These counters show a large reduction in entries into compute_style while retaining traversal visits and the correct observed value. They support the intended conditional-styling behavior. They do not mean10006 full declaration cascades were avoided: broad already reports extensive style reuse, and elementsStyled counts compute_style entries before reuse. The output has no root/element/process/phase IDs; the temporal capture and matched fixture support attribution, but no exact phase claim is made. Background work could enter the output interval. No browser-wide speedup is established.

The exact setup/action/cleanup sources are pinned in FUNCTIONS.json and match sealed probe0d782d56. The action has no await or root getter between the seek and first target getter. stdout BEFORE/AFTER and offsets preserve every byte; ACTION logs are exactly their suffix difference. Cleanup occurred only after capture. Logging affects timing, so this run supplies counts rather than timing evidence. The separate cost runtime supplies uninstrumented directional timings.

Both applications were verified across all8326files before and after; PRE-ARCHIVES equals POST-ARCHIVES. Actual preparation34ac19/session6859/5eddd4/0. Actual independent calibration/count/archive assessment and owned-profile cleanup24f51f/session74383/49dd71/0. All browser sessions closed, connector reset without launching installed Firefox,68632164bytes of two owned profiles removed after process absence and identity checks. Native source, shared app and Git index were untouched. No profiler recording or profile JSON analysis was used.
