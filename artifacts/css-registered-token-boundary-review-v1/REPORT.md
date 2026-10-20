# Fix81: independent native and WPT review

**Native/source and paired browser recommendation: accept the narrow token-boundary repair.** Standalone source packaging is accepted; isolated upstream runtime remains untested. Formal component acceptance is a separate gate and is not asserted here.

## Reviewed result

The corrected37-case WPT has27 PASS / 10 FAIL before the change and37 PASS afterward. I independently reconciled raw outcome records to both receipts, checked the unique test roster, and derived each of the10 original failure predictions from the source and independent token oracle. The candidate suite also has271 additional passing subtests, for308 PASS / 18 harness OK in total. The 271 additional outcomes were independently compared by exact test/subtest key against the prior fix80 candidate (253) and segment-provider run (18): all are unchanged PASS. Including the 27 passing new-test controls, there are 298 unchanged passing outcomes.

The candidate records68 input pins. Onlyvalue.rs and the rebuiltFirefox/XUL binaries differ. Reviewed formatted candidate SHAfd2b72943646fe84c22a16e21f21b8f890fc2782bc77e7db54d93db4d125ee93. Landing WPT SHA99bfdbf9f19063de13e609ac4d5ae2b3ebeb22484e84dde289f43a8d1178ac0e exactly matches expanded-v2. Build and WPT exit 0. The build log retains its export-monitor KeyError traceback and ends with a successful build; this is not presented as a trace-free build.

The initial native v1 did not compile: the parser destructor kept a borrow alive across moving css. v2 adds `drop(input)` before that move and otherwise preserves the reviewed candidate. No successful execution is attributed to the failed attempt.

## Native repair

The original generic-type summary misclassifies LengthPercentage dimensions/functions as Percentage; list metadata also takes both endpoints from the first component. The repair serializes once, then derives actual first/last top-level token classes with a fresh parser. Complete changed method and surrounding original/candidate files were reviewed.

Universal values still return their unchanged clone. Empty typed output produces Nothing/Nothing. Whitespace is retained; comments are skipped by `next_including_whitespace`. Strings remain a single token with closing quotation boundary. Function and all block openers produce final Other because subsequent parser calls skip their nested contents and matching closing delimiter before the next sibling or EOF. Later siblings replace the last class, so lists no longer borrow their final class from their first component. The parser's complete next/skip control flow and token classifier/separator table were inspected. Valid balanced typed serialization is an explicit admission; this helper is not a general malformed-string validator.

The patch leaves payload serialization, equality, attribute taint, URL data and the global separator rules alone. It adds one tokenizer pass over already-serialized bytes. The traversal is linear; nested-block skipping can use storage proportional to nesting through SmallVec. No allocation-free, constant-memory, page-performance or quantitative throughput claim is made.

## Test legitimacy and rejected evidence

The [independent oracle](../css-registered-token-boundary-oracle-v1/REPORT.md) establishes registered serialization-to-token substitution, dimension/ident separation and the font grammar. Font tests calibrate inherited 100px, assert computed provider value, declaration admission, final size and serif family. Absolute 20px avoids font metrics and relative-unit cycles; percentage 25% resolves to 25px from the 100px parent.

[Box3 margin shorthand](https://drafts.csswg.org/css-box-3/#margin-shorthand) assigns the second value to the right margin; its percentages use containing-block width. [CSSOM resolved values](https://drafts.csswg.org/cssom-1/#resolved-values) supplies the used-value observation for these displayed blocks. The calibrated 200px parent yields 20px from 10%, or 21px from calc(10% + 1px). The third auto value is bottom, so it cannot absorb the horizontal remainder or explain the rightmargin expectation.

Leading@ tests require delimiter @ followed by the computed value's first token. Function starts require an intervening comment under [Syntax serialization](https://drafts.csswg.org/css-syntax-3/#serialization); dimension/percentage starts permit no comment. The regex accepts any intervening comment content and permits optional comments for numeric controls, rather than demanding one engine's exact empty-comment spelling. Provider serialization is checked first. There are no feature-availability skips.

**All five leading@ cases in expanded-v1 are rejected as evidence.** Literal @var(...) is an at-keyword followed by a block, not a var() function. Expanded-v2 fixes precisely that setup by defining --prefix:@ and using var(--prefix)var(--lp). The unregistered calc and numeric controls pass in corrected baseline; the two registered function-start cases fail. The reviewer checker verifies the exact fixture delta. The invalid fixture history remains retained.

## Standalone and formal boundaries

Comparison with the retained authenticated upstream 976279 value.rs shows historical differences only in earlier animation taint OR, from_computed visibility/doc and is_attr_tainted accessor. None is needed by the new boundary scan. Minimal packaging should contain only the value.rs boundary change and this WPT; the root packaging script and receipt were read in full and authenticate exact two-file application/reversal on both bases. The reviewer independently transferred every original→candidate edit by unique unchanged source context into the retained upstream source; the resulting complete file exactly equals upstream candidate SHA70bfed7f57e06900668a96ce2002a7210d311fd89b9b8d2935ba83b5094657a8. The packaging script was not executed by this reviewer because Git operations are root-owned. No isolated upstream runtime is claimed.

The formal producer's draft summary theorem relates an abstract source-shaped event loop to endpoints of an independently flattened token-class sequence. This is useful but does not itself prove byte tokenization, generated ToCss validity or native source translation. Actual parser extraction/witnesses, assumptions, mutations and authenticated final replay will receive a separate review after final pins. This report does not accept that unsealed component.

## Recheck

`python3 -I -S check.py` authenticates retained inputs, reconciles raw outcomes, checks the 37-name prediction roster, validates 68 pins and the exact corrected fixture delta. It performs no browser/native builds. Primary specs and source/test inputs have exact hashes in SPEC-INPUTS.json and INPUTS.json. No reviewer production/WPT/Git/build/browser mutation occurred.
