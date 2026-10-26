# Fix132: refresh contributing keyframes before commitStyles

Accepted as one standalone conformance fix, pending installation in the main working tree and a signed commit. The patch contains only EffectCompositor.cpp and two WPT files; it has no pending-fix prerequisite and was tested on pristine upstream base976279105b2e78b8666a959eb3f25c9176cefaf8.

commitStyles could compose stale computed endpoints after their dependencies changed. Refreshing only the committed effect's base left contributing lower effects stale. The repair rebuilds the contributing prefix using the already-flushed full style, holds strong effect references during refresh, rechecks cascade state and composes the same prefix. A new implicit/additive case committed5px instead of280px before the repair.

The clean original/candidate/restored comparison is64PASS/12FAIL →76PASS →exact64PASS/12FAIL, plus two passing crash tests in each phase. All17 landing cases pass and all59 upstream subtests/two crash outcomes remain unchanged. Both builds, root preservation and independent terminal review pass. Exact-body WPT lint and clang-format22.1.8 pass; formatting leaves native bytes identical. The three-file patch applies and reverses in scratch.

The local timing experiment shows a cost: with32 effects, literal total medians rise4→6→4ms and variable medians5→7→5ms per16 calls. All324 rows are retained. I accept this measured explicit-API tradeoff for the correctness repair; no safe broad skip follows from the current cache representation. This is not a universal performance guarantee or a measurement of per-frame animation overhead.

The existing Lean refresh theorem covers the ordered-prefix and implicit-operation abstraction under faithful current resolver/context assumptions. Browser experiments establish the concrete observed repair. General active dependency chains/cycles, provider freshness and complete native refinement remain open. No additional theorem or CSS coverage credit is claimed for the implicit mapping.

The original clean source and build are restored. Main integration, a separate preceding research commit and the standalone signed native/WPT commit remain to be completed. No push or Try run.
