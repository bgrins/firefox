# Number document library integration proposal

Apply the staged patch against standalone library commit
`56c09405cd45a3c9b333dcec747e39efaebc7e1b`. The copied overlay does not modify the
canonical checkout or Firefox Git/index. This is opt-in research tooling and adds
no normative CSS feature coverage.

## Transport and layout

The proposal reuses 28 existing canonical Lean modules. Eight previously accepted
parser/number modules move into `CssDerivation.Parser` and `Examples`. The seven
new parser JSON codec/envelope modules live under `Codec.Parser`; runtime,
correspondence and literal fixture modules live under `Examples`; CLI and cases
live under `Tools` and `Tests`. `TRANSPORT.json` supplies the exact mapping for all
62 accepted inputs. The accepted capsule's 49 historical provenance mappings are
retained in `origin/PRESERVED.json`.

Every transported Lean definition and declaration namespace is unchanged; only
import lines are relocated. The 12 separately authored independent review
boundary proofs are transferred with one import-line change and explicit credit.
They are not new proofs from this integration. Their shape-versus-semantics
counterexample and all four arbitrary-cache raw-map cases remain intact.

Only four existing files change: the opt-in facade, its authenticated dependency
registry, and the two entry READMEs. New files provide the transported modules,
source data, checker and documentation. Both existing checkers, all earlier
public APIs, Lake configuration, default CSS module and normative coverage data
stay unchanged. The exact old inputs are pinned in `COMPATIBILITY.json`.

`CssDerivation.lean` adds `Examples.NumberDocument`. The resulting facade closure
contains 55 sources, including shared CSS dependencies. The existing restricted
facade collector is reused without code changes. CLI/test modules and their
global `main` declarations remain outside that closure. The pinned Lake default
root-module/transitive-import behavior is retained; no native-library linking
claim is made.

## Execution and theorem scope

The actual-file runner parses JSON, checks the separate `css-parser-ir-v1`
envelope and expected `NumberShape`, and executes the returned parser. It does
not dispatch to a hardcoded number program based on a profile name. The changed
valid file changes parsing behavior, despite retaining the same shape.

JSON carries the typed parser/control program. The fixed ordinary-Lean
`NumberTransfer.project` performs numeric projection afterward; that calculation
is neither serialized nor newly lowered. Only the pinned file is proved equal to
the accepted CSS number tree. The exact Int significand/scale and caller premise
remain unchanged. Alias/profile orchestration, text parsing, duplicate-text-key
policy, source-map meaning, prose translation and native floating-point behavior
remain explicit boundaries.

## Scoped integration gates

`number_check.py` authenticates installed files, reverses import relocation and
requires exact equality with the accepted 62-input source manifest. It runs the
unchanged 325-audit semantic harness, including 84 actual-file rows, nine refusals,
four compiling semantic mutations and three provenance controls. It then fresh
compiles/audits the relocated layout: 325 accepted declarations plus 12 credited
review proofs, totaling 337. It requires exact equality of the accepted axiom
sets, executes both actual files through the installed CLI, authenticates/builds
the 55-file public facade and runs the opt-in Lake target. Missing/changed parser
dependency controls exercise registration rejection.

`replay.py` copies only `base/` plus `overlay/` from its source allowlist into a
fresh temporary tree and invokes the installed number checker. Build outputs are
removed afterward. The 79-file base is a scoped snapshot, not a copy of the
hundreds of unchanged default CSS modules. Earlier 143/160 semantic inventories
remain separate and overlapping; they are pinned unchanged, not re-counted as
new CSS coverage or automatically rerun by this gate.

Root-owned post-application gates are unchanged normative registration, the
actual default Lake build, opt-in Lake build and installed number CLI smoke.
Report existing canonical cache reuse separately from the fresh scoped replay.
Repeat earlier full checkers only if changed inputs or review concerns justify
it. Preserve the recorded untracked `.DS_Store` bytes and verify the expected
patch paths against `CANONICAL-STATE.json` before signing. Root owns application,
final review and commits.
