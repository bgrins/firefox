# Source-matched repeated-visit witness

The complete formatted namespace candidate-v2 sources are retained under source/. This lead also exists in the prior name-only algorithm: it concerns slot state and repeated graph visits, not namespace lookup identity. No novelty claim is made.

The shortest graph witness uses one unregistered custom property:

```css
--out: attr(x type(*), 13px) attr(x type(*), 37px);
margin: var(--out);
```

The DOM attribute is `x="attr(x type(*))"`.

1. `traverse(Custom(--out))` allocates the root's index. `visit_value_references` first visits x, lazily loading its raw value.
2. `traverse(Attr(x,nullNamespace))` allocates an index. Its self-reference finds that same occupied index; `visit_link` sets self_ref. Popping the singleton SCC takes `VarInfo.var`, setting it to None, and `handle_loop` stores the explicit invalid entry through remove_attr.
3. The second sibling reference to x calls get_attr().is_none(). Both a missing entry and the explicit invalid entry satisfy this condition. It reloads x's raw self-reference from the unchanged DOM attribute and overwrites the tombstone.
4. `traverse` sees a value with references, finds x's old occupied index, and returns it. It does not re-traverse or reapply x. `visit_link` ignores the earlier index because its VarInfo.var is None. Thus the slot can hold an unresolved value while its index is already finished.
5. Resolving --out then looks up the resurrected raw value. Type(*) accepts the function tokens as universal syntax; the Attr substitution branch does not recursively substitute those map tokens again. Expected source prediction is leaked unresolved tokens in computed --out, with invalid downstream margins.
6. Separate top-level custom declarations invoke Context::reset between roots. That clears index maps, count, var_info and stack, so a newly reloaded cyclic attribute is traversed again. This is why the independent-declaration control should recover the expected fallbacks.

The noncyclic failed-substitution row (`x="var(--missing)"`) tests the same finished-node/tombstone mechanism without SCC self-reference. Constrained type(<length>) rejects leaked function tokens and can mask the state defect by using the fallback. Literal values and independent self-cycles are controls. The same raw cyclic value under two attribute names exercises a shared repeated dependency, not a presumed passing control.

Predictions require browser confirmation. The new source admission task will prove allocator invariants separately; injective index allocation does not itself establish that finished nodes can never contain unresolved values.
