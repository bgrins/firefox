# Move context through shadow boundaries

This focused companion models the committed, still uncompiled shadow move-context proposal. Eight standalone Lean claims passed the actual kernel, and two deliberately false claims were rejected. It does not establish native refinement, browser repair, or new canonical coverage.

A path has arbitrary length and mixes light edges with shadow boundaries. A shadow edge constructs fresh local root, original-parent, document and binding facts; the policy controls only whether the incoming move bit is forwarded. The correct traversal preserves that bit through any nesting. Ordinary false remains false. Both correct and broken traversals have the same independent root facts, so unchanged shadow-root identity alone cannot certify correct move handling.

| Claim | Scope |
|---|---|
| forwarded_move | Arbitrary light/shadow paths retain the incoming bit |
| ordinary_stays_ordinary | Both policies preserve ordinary false across arbitrary paths |
| facts_independent | Structural context projection is independent of bit forwarding |
| fresh_shadow_fields | A shadow boundary uses its own supplied root/parent/document facts, with false binding root-change/uncomposed-document flags |
| moved_callback | Both traversal phases preserve the bit and a present move callback selects only moved |
| absent_callback_fallback | Missing move callback selects the optional disconnected/connected fallback |
| unchanged_animation_obligation | A preserved bit supports an abstract token obligation only with unchanged animation applicability |
| shadow_loss_witness | Nested shadow traversal can retain all root facts yet lose the move bit and select ordinary reactions |

FalseFlag rejects preserving true after a boundary that resets the flag. FalseOuterRoot rejects copying the outer root into the new shadow context. The unchanged-animation argument is an explicit environmental assumption, not derived from root identity. `retainedAnimation` is a stipulated consumer obligation by definition, not a proof that the animation engine preserves objects or timing. `none` means no preservation conclusion, not proof that an animation must cancel.

The callback model assumes a connected, already-custom element and a removal/binding pair. It models callback selection rather than reaction queues, scheduling, exceptions, upgrades or JavaScript behavior. Facts is an abstract projection of separate BindContext and UnbindContext fields, not a claim that Gecko has one combined structure. A shadow boundary's supplied original-parent/document facts must come from the native constructor; the theorem does not justify replacing them with the host's outer context or prove that an arbitrary supplied document describes a valid DOM. Path membership is assumed to follow the actual shadow-including traversal; DOM validity, slot assignment and a complete native tree correspondence are not proved.

The native map and current signed source hashes are in SOURCE-JOIN.json; primary specification reads are recorded in SPEC-READ.json. The source proposal and 17-case system-browser WPT evidence remain separate immutable artifacts. The system observations are not an executed local candidate, and known upstream custom-element failure coverage is prior art. No bug, native acceptance or proof-coverage count is added here.

Actual replay: `python3 -I -S -B artifacts/css-shadow-move-context-model-v1/replay.py run-1`, tool62a9eb/session98575 →9eec03/0. Context and axiom audit passed; FalseFlag and FalseOuterRoot failed for their intended false propositions. The pinned Lean executable ran only in private temporary scratch; all generated oleans and scratch were removed. No native source, Git index/ref, canonical epoch, Gecko build or browser mutation occurred. No `sorryAx` or `Lean.ofReduceBool` is admitted by the audit.
