# Source and specification mapping

The [DOM move algorithm](https://dom.spec.whatwg.org/#concept-node-move) invokes moving steps for shadow-including descendants and independently identifies the moved subtree root. For eligible custom descendants in a connected destination it requests the move callback. It does not substitute ordinary insertion/removing steps. `walk` abstracts one path within this traversal, not tree validity or mutation ordering.

[HTML callback reactions](https://html.spec.whatwg.org/multipage/custom-elements.html#enqueue-a-custom-element-callback-reaction) use disconnected/connected fallback only when the move callback is missing. Each fallback callback is itself optional. `reactions` includes both unbind and bind phases, so preserving the bit only on binding is insufficient to eliminate an earlier disconnected reaction.

[CSS animation persistence](https://drafts.csswg.org/css-animations-1/#animations) depends on applicable animation names and keyframes; matching updates retain playback position. `retainedAnimation` exposes unchanged applicability as an assumption. This is an obligation model, not an implementation of CSS animation matching, identity allocation, rendering or scheduling.

| Native name | Abstract projection and limit |
|---|---|
| Element::BindToTree / Element::UnbindFromTree | Light-child calls forward their context; shadow-root calls currently omit the bit. `Edge.light` forwards context and `Edge.shadow` selects the policy. |
| ShadowRoot::Bind / ShadowRoot::Unbind | Construct fresh shadow-local contexts. The proposed change sets only IsMove before visiting children. `enter` never reuses the outer facts at a shadow edge. |
| BindContext(ShadowRoot&) | InUncomposedDoc and SubtreeRootChanges remain false independently of IsMove. Their false values in shadowFacts do not mean an ordinary operation. |
| UnbindContext(nsINode&, BatchRemovalState*) | Root/original-parent/document facts are constructor-derived. The real shadow-root parent is null; the model allows a supplied Option parent so preservation of that independent value is explicit. |
| Element custom-element lifecycle selection | IsMove selects the connected-move route; ordinary unbind may issue disconnected. The model assumes custom/connected guards rather than proving them. |
| Element animation-collection clearing | Non-move unbind reaches the clearing branch; move forwarding avoids that branch. Avoiding this one branch is not a full proof of animation persistence. |
| FragmentOrElement unlink / ShadowRoot::Unattach | Ordinary callers retain false by default. ordinary_stays_ordinary rules out manufacturing a move bit. |

Current signed HEAD 2fe2ced22a525a4348286bddaa7dcb0168d72905 matches all six sealed source/context bodies used here. Fresh Searchfox definitions of ShadowRoot::Bind and ShadowRoot::Unbind and bounded Element/UnbindContext searches corroborate the named map. Searchfox indexing is distinct from the exact immutable local Git join; no generated line permalink or source-revision equivalence is claimed.
