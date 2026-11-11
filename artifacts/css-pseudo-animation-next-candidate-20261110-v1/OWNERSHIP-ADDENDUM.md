# Captured pseudo-request aliasing

Addendum to the frozen snapshot source report; native patch b37e4885614c5b2acb7fa4320ca734fd2c7fa1062e12f5b55c6e60be71d25166 is unchanged.

KeyframeUtils accepts const PseudoStyleRequest&. Before extraction that reference points into live mTarget.mPseudoRequest. After extraction it points into the owned snapshot's copied request. The element pointer already has value semantics at call entry; the new OwningAnimationTarget also retains that element's lifetime. The pseudo-request change stabilizes its value as well as its lifetime.

Thus hypothetical reentrant retargeting during property conversion could previously change the request seen through the live reference, while the captured request remains paired with its captured element. This coherence is intentional for request-local inputs. The source audit does not prove observational equivalence under arbitrary reentrancy, nor that every declaration/provider/context is immutable. Ordinary preservation is scoped to the current synchronous preparation path and requires native build/regression evidence. A final CSSOM caller still needs a no-flush/no-script or explicit revalidation contract for target, pseudo, style, timing and provider state.

The new ownership does not publish renderer state or make the snapshot a complete deeply immutable effect. No source or runtime patch changed for this clarification.
