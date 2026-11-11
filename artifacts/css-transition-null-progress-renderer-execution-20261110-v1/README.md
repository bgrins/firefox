# Release-browser transition routing observation

Firefox 158.0, through the separate System Firefox DevTools session, ran the exact standalone page and shared JavaScript recorded in INPUTS.json. The objdir candidate browser was not used.

All 53 setup/identity checks passed. All 36 computed-style reads were recorded. Transition-only remained 0.5 in every phase. Active overlap produced 0.5, 0.8, 0.8, 0.5 before insertion, during overlap, after two animation frames, and after cancellation. The current before-phase/fill:none case produced that same sequence despite unresolved animation progress. Its original transition remained present, targeted the same element, and stayed paused at currentTime 500000 with progress 0.5 throughout.

This establishes observable release behavior, not yet a specification violation or a new independently triaged bug. The unresolved question is whether an effect with no sample may choose the insertion origin of another effect's composited value. The active overlap control intentionally expects author-important 0.8; ordinary transition-only expects transition 0.5.

BROWSER-RESULT.json contains explicit JSON.stringify serialization obtained from the browser. The first raw tool response represents repeated object references as empty objects in some positions; explicit serialization preserves those timing records. Both raw responses are retained. Executed input hashes were rechecked after execution. The unexecuted WPT wrapper gained additional JSON diagnostics during the run, recorded in INPUT-FREEZE-NOTE.json; no WPT-harness execution is claimed here.

Cleanup reported zero probe elements and zero animations. A tab-close call used the wrong parameter name and was rejected; the following close-session call confirmed closure of the entire tool-owned Firefox instance.
