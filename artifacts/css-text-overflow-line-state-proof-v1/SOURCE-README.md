# Ordinary text-overflow line-state source package

Run `python3 check.py --out /tmp/text-overflow-line-replay-unique` from this
source directory. The output directory must not exist. Default replay rebuilds
all native capsules, executes both full models and semantic mutants, and checks
Lean proofs and executed counterexamples. It never runs Firefox or changes the
checkout. `--native-only` is a development subset, not the acceptance replay.

Copy every path in `REPLAY-INPUTS-v1.json`, preserving its relative path, plus
that manifest itself. This file is the source-package entrypoint. No historical
browser evidence, report, frozen receipt, compiler output or generated fixture is
required. `NATIVE-BINDING-v1.json` includes complete retained source contexts,
including the nonexecuted caller audit; those snapshots are in the manifest.

The pinned Python, selected Xcode compiler/SDK and Lean executables must be
available at the paths in `TOOLCHAIN-v1.json`. This is a source closure with
explicit external tool requirements, not a hermetic toolchain distribution.
The compiler uses UBSan with nonrecovering diagnostics and lifetime warnings.
The script verifies source and executable identities before running them.

Scope: exact extracted ordinary-line native analysis under owned geometry,
font-measurement and frame adapters; full bounded state/trace agreement with
independent logical interval/cluster models in Python and Lean. Lean's universal
finite-line theorem is definitional normalization, parametric in a deterministic kernel and stable coherent
measurement cache. The actual process preparation is linked by a separate no-clamp lemma.
Pre-entry debug records and clip/clip fast returns are outside that equality;
replay reports output-only and final-state comparisons separately. Complete native refinement, shaping/reflow, all writing-mode
conversions, renderer behavior and arbitrary clamp sequences are not proved.
Synthetic clamp cases remain diagnostics. The immutable-cache premise includes
cached ellipsis allocation failure; changing the provider between calls violates
it. Model fuel is a checked bounded-execution limit, not a universal native
termination proof.

The model treats display-list prune/create calls as nonmutating observations.
Root browser evidence is separate from this source replay. Its strict same-glyph
WPT references pass; the earlier rectangle raster rule retains one corner pixel
requiring separate interpretation. Do not infer a renderer proof from the trace.
