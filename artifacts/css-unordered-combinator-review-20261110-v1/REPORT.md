# Independent unordered-combinator implementation review

Accepted for the bounded research milestone. No blocking finding. This review checks the completed implementation against the unchanged pre-proof contract and the separate pre-proof critic review; it does not certify mechanical derivation from CSS prose or browser conformance.

## Authenticated inputs and execution

Author SOURCE-ONLY.json: `860df6b0094d748afdce3f94c6d427d53eecac369c02ef1c4266a8e397a82823` (54 inputs). The pre-proof PROPOSAL-FILES.json pins the same CONTRACT.md, specification excerpts and 38-word oracle. All 206 author inventory entries were authenticated after the author announced terminal freeze. The preserved grammar/parser and compatibility copies were independently compared to their local source artifacts, beyond the replay's internal copy hashes. Remote Git/source-server authenticity is not re-proved here.

Critic report: `../css-unordered-combinator-contract-review-20261110-v1/REPORT.md`, SHA256 `4ba446452e29c6aa7017fa185181121859eb0b31c5b1dd4591f5d525c460ddbb`. Author final REPORT.md: SHA256 `eb2a744d26ebef857c7714fced9e780bd0f3e6c8d38debe09cb49b764c1e8917`.

Fresh allowlist-only replay passed: 15 modules, 69 main audits (56 new, 13 preserved), 1,559 text-transform rows, 70 old compatibility rows, 17 shape rows, three changed-file rows, 18 source/notation refusals, 12 JSON/domain refusals and three compiling semantic mutants. The semantic report exactly matches the author's terminal source-only result. All 55 command output hashes were independently checked; the 18 nonzero exits are the 12 expected decoder refusals and six baseline-witness/unchanged-law rejections. All 1,649 actual-file result rows have exact list/string/Boolean types, not merely Python equality with expectations.

`Boundary.lean` adds nine separately kernel-checked and axiom-audited boundaries: three equal component occurrences versus a fourth token, left-nested contiguous acceptance versus interleaving, repeated trailing suffix preservation, nullable alternative refusal, an invalid inner node that an outer optional cannot rescue, exact saved stack suffix, and a direct nullable semantic derivation outside the implementation's admitted domain. An independent category predicate checked 9,331 sequences through length five against the frozen oracle. No implementation enumerator/parser generated that predicate.

Both fresh compiled scratch trees were removed. Command logs and hashes remain. No canonical library, live native source, Git/index, browser or native build was changed. Reproduction commands are in README.md.

## Proof and interface assessment

`UnorderedMatches` quantifies nonempty `List (Fin children.length)` with `Nodup` and chains the preserved inductive `Matches` relation through intermediate remainders. It does not reference `orders`, `plans`, `lower` or executable run. Index identity allows equal grammar texts to remain separate occurrences. `orders_spec` assumes a duplicate-free source; its specialization supplies the duplicate-free bounded index range, so it does not assume unique child texts.

`plans_spec` joins the independent index semantics to finite enumeration. `lowering_spec` and `run_spec` quantify over arbitrary grammar lists and input/remainder lists, carrying the explicit admissibility condition. These are useful generic soundness/completeness results, not examples or a renamed lowering-membership predicate. The nullable theorem establishes an empty complete match, while the support guard deliberately excludes such operands. The independent nullable boundary confirms that the semantic relation and implementation domain are distinct. Suffix laws use the established primitive grammar relation.

The postfix step consumes exactly the reversed child prefix and preserves the remaining stack. `unordered_step_matching` connects this actual execution boundary to the independent relation. A refused nested node propagates via Option binding and `rejected_prefix`. The Python parser retains n-ary same-level groups and explicit nested groups; it refuses unsupported && and references. Grouping/precedence correctness of Python extraction is reviewed and tested, not proved universally by Lean.

`legacy_execute` universally preserves every old typed opcode list and arbitrary initial stack; `legacy_decode` and `legacy_encode` provide the corresponding old interface laws. Historical interpreter/parser source bytes remain unchanged. The theorem does not promise equivalence of all arbitrary JSON spellings or preserve the previous rejection of double bars in the new opt-in reader.

`text_json` uses the actual Lean.Json adapter and checks the quoted extracted value, while `text_decode` checks the typed program. `text_language` proves list permutation with the pre-proof oracle, with separate size and distinctness proofs; `text_accepts` and `text_remainder` extend this to arbitrary normalized tokens and suffixes. The generated grammar's getD fallback is not hiding failed decoding: `text_decode` explicitly establishes successful decoding. Generation, quotation and serialized-file equality are checked by Python. RunnerV2 imports only JsonV2, not the property fixture/oracle, and executes the supplied JSON file. Changed-valid execution confirms that dependency operationally.

## Controls and remaining limits

Every declared theorem in the reviewed modules is included in the 69-name audit; only standard propext, Quot.sound and Classical.choice are allowed. No sorry, new axiom, unsafe or native_decide is admitted. Each semantic mutant first compiles the altered implementation, breaks unchanged laws, and satisfies a specific altered-behavior witness that fails on baseline. Unchanged-law diagnostic failures alone would be weaker evidence; the separate kernel witnesses make the claimed semantic differences concrete. The three additional witness axiom audits are separate from the 69 main audits.

Language/remainder membership is proved, not output multiplicity/order. Nullable complete operands, &&, other multipliers/productions, arbitrary Bikeshed processing, raw CSS tokenization/case folding/escaping, CSS-wide keywords, variable substitution, rendering and Stylo remain outside scope. The fixed JSON-value theorem is not a generic JsonV2 accepted-input schema theorem or proof of Lean.Json.parse. The reviewed English interpretation remains a human assumption. Factorial ordered-subset enumeration has no production performance claim. No unsupported generalization was needed to accept this milestone.
