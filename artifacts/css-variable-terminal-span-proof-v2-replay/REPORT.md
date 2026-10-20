# Terminal-span v2 replay

The sole changed predecessor input is check.py: execution-mode rejection now precedes imports except builtin sys. All 16 other predecessor inputs, including every Lean module, audit and native source/binding, remain unchanged. test_integrity.py and V1-DELTA.json are added. v1 remains immutable; V1-UNSAFE-SHADOW.json retains the independently reproduced reason for replacement.

Fresh canonical and manifest-only relocated replay each pass 37 exact axiom reports, 10 complete source bindings, candidate semantic checks and five compiled model mutants with intended exit-42 mismatch labels. Twelve integrity challenges reject before output, including -O/-OO, nonisolated, site-enabled and the exact pre-import json shadow marker. The shadow marker never executes in v2. Test orchestration is invoked with -I -S; no unrestricted execution guarantee is made for that runner.

No mathematical, provider, native correspondence or serialization scope changes. The source REPORT and all previous admissions remain binding. Completed owned compiler targets were removed after logs/results were retained; CLEANUP.json records exact paths/hashes/sizes. No native/Git/browser/Firefox-build changes.
