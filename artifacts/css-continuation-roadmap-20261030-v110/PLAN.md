# CSS and Stylo continuation

HEAD ecfe313d582a: 149 accepted native fixes, plus two test-only repairs. Goal active. This turn completed an actual broader baseline, extended the spec-supported target set, corrected a source-supported gap in the proposed repair, and started its first native build. No new commit or push; signing still awaits 1Password readiness.

## Active native experiment

V3 candidate on the exact 74-case suite is running: session72027, launch67e6f7. Owner css-prioritary-selection-candidate-v2, active FILES238938ba1fab12f3d759e901dcba57afa9bdbd383d2212a65833926cef12dfec. Runtime css-prioritary-selection-candidate-runtime-1; full log in css-prioritary-selection-candidate-v2-root-activation/RUN.log. Root preflight7a4547/0, activationc66f62. Poll this exact handle; do not run other native/app/index operations or commit while its overlay is active. Native compilation succeeded. Completed ordinary lane:52 PASS/16 FAIL, all13 ordinary targets PASS (nine improvements), but one original PASS regressed: Selected identifier color-scheme dependency: union-plain. Its preservation/repair gate is false. The forced-color browser has finished its log but its lane receipt and Mozilla lane are still pending. The full owner has no terminal yet. Source-review agent is investigating the regression using only completed ordinary evidence. Disabled candidate terminal reviewer is sealed: FILES025c5985194eb6086dcf0dfcfa1ea077265534da9657fb3d47696b81d18afa8f; root read exact deltas and authenticated owner payloads (a54012/0). Bind actual terminal only after72027 ends.

The exact two roles are clean provider8a4adc90 plus cascade V3beaa48e574b51915fb0ac9fc13b31158016b0b05c7baa67cf41d146886d8909e; restoration returns held provider2675 and original cascade2cc7. No selected-color helper overlay or intermediate-guard optimization is included. Fifteen explicitly named targets contain four original passes and eleven failures; preserve all46 original passing callback signatures and all11 page endings. Complete observation/restoration remains separate from a false repair gate. Full85-signature equality is a separate diagnostic; intended improvements will change it. The old forced-auto fixture remains exact and cannot substitute for the later matched-reference test.

## Verified original74 baseline

Actual original99665/31e9ed/08b9e2 exited0; independent reviewer4433/018000/6cf122 exited0. Frozen runtime css-prioritary-selection-original-runtime-1 FILESbcf99141fe5cb707c6d7983084d33ceadd68ef06af10ae598acb0903ddd8c275 (159 payloads). ROOT-REVIEW SHA7a39ac355bec0701d0dea0b36ec4d464bb3c875e5bac7acd94d6fe8f252eb945, owner RESULTcf490788d3b62616bbb5da22d61ec9419d307fa533f1bbced4d0f9031e3c17aa.

| Actual lane name | PASS | FAIL | Pages OK |
|---|---:|---:|---:|
| ordinary |44|24|8|
| forced_colors |0|3|2|
| mozilla_appearance |2|1|1|
| Total |46|28|11|

The real HTTP Zoom capture and independent postcleanup replay succeeded. All49 earlier original45 signatures remain unchanged. Config mappings, exact metadata, test resources, native source/binary provenance, source/application/index restoration, process/profile absence and removal of the1,008,605,176-byte backup were independently verified. Root freeze90450d/318cb1/0 refreshed only raw-index bookkeeping.

Five known overridden-declaration failures reproduce. Four extra ordinary failures involve winning-variable, fallback-revert, fallback-revert-layer and fallback-revert-rule. A new primary-spec trace reaches their endpoints:40/60px, except plain revert22/34px. See css-prioritary-rollback-expectations-spec-trace-v1 (FILES11894e7c34c22e4a8f23b20122bd061fe180b68a1336acd3403607b3fc488a0c). It is a manual specification trace, not native correspondence or first-getter proof. Forced-color none and Mozilla earlier-author-winner also fail with incorrect registered defaults. These are witnesses, not established distinct bug counts.

## Broader validation still required

Source review found a reachable potential V2 regression: Appearance asks itself to establish its unavailable appearance gate, creating a self-edge. V3 adds only the Appearance exclusion to that gate-dependency branch. Parser/stylist reachability is captured in css-prioritary-appearance-parser-source-v1. Proposal css-prioritary-selected-declaration-proposal-v3 FILES832d247da7050b1038bcf1b96a8fa72fa2cef9f63c2f514da37fc182de9cfbc6. Three new Mozilla controls are sealed in css-prioritary-appearance-self-probe-v1 FILES4effa8f9a40c16fcba3c714f02a9d18dd59f0c8a4808d4fd43ff840f67a79c12. Predicted V2 regression remains unobserved and is not a shipping-bug credit.

Forced auto currently combines the dependency-defaulting defect with existing test51's computed-scheme failure. Merely removing the scheme assertion would not guarantee matched used schemes. The revised fixture adds a separate registered literal reference with the same forced-color-adjust:auto and phase scheme, retains the normative reference diagnostically, all target samples, none's scheme assertion, and unchanged51/metadata. Matched fixture FILES1d737d900c41bf53bb7414e62511f77c50f8161c19210681ea3e0471a3394a79; no browser outcome yet.

Use css-prioritary-selection-suite-v3 FILES512390cecca0942d0bbe7cb3f21ee4f5878b27ae9350828be3c31f2c771a42f0 for fresh original77 and candidate77:77callbacks,12pages,89signatures,16resources; lanes68/8,3/2,6/2. It explicitly replaces the forced page in suite-v2 and retains all other bodies, metadata, Appearance3 and Zoom requirements. Existing74 or old77 data cannot be relabeled as its baseline. Typed agent is preparing original77 with the reviewed intermediate guard, current bindings disabled pending actual candidate74 restoration.

## Guard performance proposal

Archive map contains29,278 files totaling2,654,777,370bytes; per-call dedup saves only153 of30,534 reads. Proposal css-prioritary-intermediate-guard-proposal-v1 FILESff5307801290a210780500d66f06f4a44ac5619894e0065be9ba650a8afde198 retains full admission/pre-overlay/final/independent archive sweeps and all mutable pins, staged values, identities, indices and consumed inputs. Intermediate snapshots explicitly mark the archive not rechecked and lack the full-preservation flag. Twenty negative tests and peer review passed. Future original77 must bind/review the concrete transitive input closure; owner self-pins derive from authenticated FILES/invocation digest to avoid circular hashes. No optimization was applied to current74.

## Verified pretrial restoration state

CURRENT-EPOCH607c07bbe4964546b86ea3e6558da26640f6acc957e629dd5f4fa9134b3cd3e7, rawindexf64aadec3a1bc7f2211e0baad7e12e063d7a37789b50e9ec0940f6e786829903; OWNED76bf1cf2 and ROLE96358abf unchanged. Original74 ROOT-REVIEW contains exact hashes/identities. Application entryinode280041640 and target280058763, unchanged SHA936bd88f/BuildID20261029165244/revision20ab7e723b663c0f78c8490e60a6fccc5e65cc99. Held provider was sole tracked edit before current candidate overlay; staging empty.

## Commit and other milestones

The shared union/image prerequisite already reproduced all49 original signatures in its independent native trial. Isolated union38/7 and image37/8 improvements are disjoint; narrow combined45/0. Independently based bug patches can use the shared prerequisite, with parent-specific cascade hunks for composition; no signed commits yet. Min/max and explicit-base logarithm fixes also await their separate signed native+WPT publication after research. No unsigned fallback or automatic repeated signing attempts; the asynchronous readiness question remains unanswered.

Selected-declaration Lean model remains11 audited theorems/six rejected false controls, without native correspondence. Earlier Bloom milestones1–6 are complete only within their recorded bounds. All-CSS verification is unfinished. Latest untracked auditv20 (96a962/33ad6c/0):563 expected, no added/missing paths;68 project bodies match actual HEAD recovery blobs,495 unrelated paths/metadata unchanged, nested Lean only.DS_Store. SHA d4987890f259ad03d31517eac0dda2dd9353ea9ecb82b6f83aef3d2187a63b8c. Staging empty; cascade is the only tracked edit during the active candidate overlay. No untracked deletion was performed. The audit excludes ignored research/build output and does not inspect unrelated file contents.
