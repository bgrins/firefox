# Flex overflow-container final-position review

Accepted: the exact two-file native/WPT patch identified in ACCEPTANCE.json.
The change positions overflow-container children after the flex fragment's final
size is known, then performs the existing overflow and status joins. Ordinary
children retain their existing vertical-rl correction. This fixes the observed
ordinary-size coordinate error without combining the wide-arithmetic prototype.

Root independently inspected the native delta, ordering argument, proof scope
and browser oracles. GenerateFlexLayoutResult enumerates principal children
before the helper in both versions; the late tracker is constructed after normal
child mutations. New current-parent continuations are excluded by the helper's
previous-parent eligibility rule. Under the existing normalized-list and valid
chain invariants, no introduced ordering dependency was found. PopulateReflowOutput
does not commit parent frame size or mutate lists. Overflow bounds and status
still merge before absolute-child finishing and shared-data retention.

The candidate WPT corrects 112 failures and preserves 224 passes. All 34 existing
regression outcomes are unchanged (24 PASS, 10 expected FAIL). Lifecycle and
external-resize probes pass; 20 opposite/orthogonal child-mode observations are
unchanged. Actual trace visits all reflowed; these observations do not establish
universal skip exclusion. The skipped branch's placement is unchanged.

The authenticated 223-payload source/formal capsule was freshly replayed from a
manifest-only relocation: 19 kernel audits, four semantic false claims, two
forbidden-axiom guards, eight extracted native cases, JavaScript syntax, raw
browser receipt recounts and standalone patch apply/reverse all passed. Separate
integrity controls rejected unexpected files, modified source, extra caches and
source-role substitution. The logs retain commands and results. The extracted
native arithmetic cases include expected sanitizer failures; they are not a
claim that the whole native implementation is free of undefined behavior.

Actual-path clang-format made no byte changes, explicit WPT lint passed with no
warnings, and the final installed build succeeded. The reviewer tooling selected
#layout-reviewers. INSTALL.json pins the installed shared source and WPT. No
signed commit has been made. Evidence and formal companions precede the native
patch in the prepared queue.

Full fragmentation, machine arithmetic, callbacks, lifecycle, and skipped-child
correctness remain open. The separate initial relative-positioning omission is
not repaired here. The browser pair used the shared combined project tree; exact
standalone patch application is checked, but isolated upstream runtime is not
claimed. This acceptance does not accept the earlier wide packing prototype.
