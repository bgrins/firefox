# Baseline cross-size sum: portable WPT correction

Accepted within the reviewed final-sum/storage scope; signed companion and separate Gecko/WPT commit pending.

Independent review accepted the native change and six primitive formal claims but held the package because its WPT required every engine to preserve12–17million-pixel input values. This new version applies the exact proposed correction: the measured input-range checks use assert_implements_optional. Once admitted, the final100px height assertion remains unconditional. The original artifact and HOLD remain immutable historical evidence.

Fresh paired local builds admit all54Gecko cases with no optional-prerequisite skips. Baseline12FAIL/42PASS becomes54PASS; all42passing status/message pairs are identical. Only the C++ source and two binary pins change between runs. Unsupported-input routing is covered by the review's separate script-control challenge, not counted as browser passes.

The final-sum repair was temporarily removed in isolation for the baseline run. All repairs, including safe-scroll and collapsed-overflow, were restored exactly; the restored build succeeds. WPT lint reports zero errors/warnings. The native patch is byte-identical to v1, and the complete changed function body matches the previously reviewed/proved formatted source and both new standalone snapshots. No new native semantics were introduced by this correction.

The exact two-file patch applies/reverses on retained HEAD and upstream. Packaging preserves the real index and worktree. Earlier34-file regression evidence for the same native source is in the collapsed-overflow artifact; the older baseline repair's29-file regression suite remains in v1. Only the WPT prerequisite changed afterward, so no broad regression rerun was needed.

Independent review tested four repaired source roles at two optimization levels across1,293cases, plus2,500old-defined controls and five semantic mutants at each optimization level. It replayed15kernel results including discovery and review lemmas. Root authenticated the closed648-file review, inspected its reasoning and required correction, and satisfied all three listed package gates. Native input providers, earlier per-item arithmetic and later multiline accumulation remain separate obligations. Clamping is not claimed identical for every previously representable value above nscoord_MAX; the documented bounded observer result is the accepted claim.

The browser evidence uses a shared local build with pinned inputs. There is no isolated upstream runtime claim and no whole-flex or security claim. See ACCEPTANCE.json and SOURCE-TRANSFER.json for exact pins and scope.
