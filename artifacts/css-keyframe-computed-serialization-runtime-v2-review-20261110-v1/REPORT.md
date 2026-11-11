# V2 conformance baseline terminal review

Independent raw/result/restoration audit passes; runtime hold released. Five FAIL now all reach getter array assertions; three controls PASS and harness OK. Lint exits 0; WPT exits 1 for the unannotated baseline failures. The wrapper exits 0 because its exact inventory/status gate and restoration pass. No native build ran.

Ordinary and registered relative endpoints return 1em/2em instead of 16px/32px. Unregistered references return var(--source) twice instead of 12px/12px; after source mutation they still return the expression instead of 24px/24px. The new explicit font setup reaches 20px successfully, then its getter returns 1em/2em instead of 20px/40px. Token, WAAPI and replaced-CSS specified-value controls pass. Actual messages and expected/known-intermittent fields match the raw JSONL exactly.

This establishes the fifth getter case without depending on v1's unresolved animated-font setup. V1 and its separate diagnostic remain preserved; no attribution of that sampling issue follows. These are related getter computation failures, not five newly counted defects.

Frozen execution manifest: 290fe4f12c09856161984acfd41a2bfdecd8797d7d898271056aab3cb0625f08. HEAD: ec467c0219d3d5daf70f42fcc53677cf8a262173. Independent checks cover nine raw records, complete lifecycle, all 9,378 application entries, three extras, retained source/test/binary/configuration pins, logical index/HEAD and clean tracked tree. Owned groups, temporary fixture/metadata, backups and lock are absent. Familiar nonfatal SWGL framebuffer/Nimbus messages remain in full logs; no harness error, crash, timeout or missing callback was found.

Root executed v2 and authored its small fixture/data delta. Reviewer authored the original wrapper and independently checks this execution/restoration, not original wrapper authorship. No native repair, catalogue increment or final missing-pseudo/debug acceptance is made here.
