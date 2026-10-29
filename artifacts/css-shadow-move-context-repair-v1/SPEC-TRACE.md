**Question:** Does moving a connected host justify ordinary removal behavior for its shadow descendants?

**Scenario:** Same connected document; the host carries its internal shadow root and unchanged animation declarations/keyframes; no display:none change; the custom element defines connectedMoveCallback. Self-reference is normalized to the next sibling, not treated as an observable DOM no-op.

1. [ParentNode.moveBefore](https://dom.spec.whatwg.org/#dom-parentnode-movebefore) invokes the move algorithm after normalizing the reference child.
2. [DOM move](https://dom.spec.whatwg.org/#concept-node-move), step 25, visits shadow-including inclusive descendants. It runs their moving steps; ordinary insertion/removing steps are not invoked. Step 25.3 queues connectedMoveCallback for each qualifying custom descendant.
3. [HTML custom-element reactions](https://html.spec.whatwg.org/multipage/custom-elements.html#enqueue-a-custom-element-callback-reaction) falls back to disconnected/connected behavior only when the connectedMoveCallback entry is null. That guard is false here.
4. Independently, [CSS Animations 1, animation model](https://drafts.csswg.org/css-animations-1/#animations) keeps an animation running while its name and matching rule remain, and updates matching animations while retaining playback time. [Animation play state](https://drafts.csswg.org/css-animations-1/#animation-play-state) preserves the progress of a paused animation. These conditions must be calibrated; moves that change declarations or display are different cases.

**Verdict: REACHED** — the connected-move callback route includes shadow descendants; ordinary disconnected/connected fallback is not selected for the defined callback. Cancellation/replacement of the calibrated unchanged paused CSS animation is also inconsistent with the cited animation persistence rules. This is a manual specification/source trace, not a formal native refinement.

Rejected alternatives: ordinary appendChild removal is a different algorithm; absent connectedMoveCallback intentionally permits fallback; changed keyframes/animation-name or display:none can legitimately alter/cancel animations. None describes the controlled shadow-host case.

Primary pages were read directly on 2026-10-28: DOM last updated 2026-10-19, CSS Animations 1 draft 2026-09-13, HTML last updated 2026-10-26 (web receipts turn2727view0,turn2735view0/2,turn2739view1). webspec-index was unavailable (5fb1d6); prior bootstrap attempts did not install it. No graph-enumeration or automated anchor-validation claim is made. Current live spec text was inspected rather than inferring behavior from an old draft or a test title.
