# Scoped hidden-measurement state machine

This artifact models the original clean measurement miss under skipped layout and the **provisional direct-item dirty mark** from source-review-v1. It does not establish that this patch is sufficient or appropriate to land. The newer proposal to dirty principal child subtrees when flex skips its child layout is a separate candidate, not this artifact's implementation.

## Contract

1. A measurement cache hit requires a clean subtree, an existing measurement, and equality of all captured key fields. A hit preserves geometry; key equality alone says nothing about whether that geometry is current or came from real layout.
2. On a miss, the modeled ordinary block's hidden-parent early return leaves the newly constructed reflow output at zero. Finish publishes that size. Hidden DidReflow preserves the incoming dirty state. Consequently a previously clean item can become zero-sized and remain clean.
3. The provisional mark makes that miss remain dirty. A later direct geometry query admits forced hidden layout only for a dirty queried frame. If the caller actually reflows the same item with the supplied forced input and its provider returns, the resulting geometry is exactly that provider's returned size, and the completed frame is clean.
4. Recovery holds for an arbitrary `Key → Size` provider; it does not assume that the provider returned a desired size. `fixedBlock` is a separately stated fixed-size semantic specialization, not a derivation of complete nsBlockFrame sizing.
5. Repeated-query preservation means that a clean query does no forced work. It is not a freshness theorem for arbitrary changed keys or providers. The caller must invalidate the queried frame when geometry inputs change. A concrete changed-size/clean-frame counterexample is retained.
6. Dirtying a measured parent does not establish eligibility for a clean queried descendant. The two-frame countermodel is an explicit remaining obligation. Valid-hit pending placement, skipped descendant layout, traversal of all child lists, and MarkSubtreeDirty's early return on already-dirty nodes are not repaired by this model.

## Native correspondence and admissions

The capsule extracts fourteen complete units: three zero-initialization constructors; cache class; original and provisional measurement methods; logical FinishReflowChild; DidReflow; both hidden predicates; and four PresShell forcing methods. It also extracts the exact leading hidden-parent/no-continuation guard from nsBlockFrame::Reflow. The remaining block algorithm is a declared provider. The three constructors are authenticated complete units inspected for their zero initialization chain, but the C++ facade supplies its own equivalent small LogicalSize constructor.

The executable facade specializes to a stable ordinary non-anonymous direct child of a single hidden in-flow parent, no continuations, horizontal writing mode, no relative positioning, no SVG/MathML/table special cases, no percent observer, no callback-driven mutations or frame replacement. NoMoveFrame retains the actual size-publication branch of FinishReflowChild. Real content/style hiding, physical/logical conversions, overflow storage, reflow scheduling, ancestor dirty propagation, property ownership and notification side effects are supplied by simplified providers, not proved.

PresShell's actual set insertion, membership, clean-frame gate, and clearing run in the extraction. FrameNeedsReflow counts a scheduled request; the document flush callback invokes the modeled item's measurement. That callback and its key are supplied by the harness. This is not a proof that a real document flush traverses this item or all descendants, terminates, or preserves identity.

CachedFlexItemData is a handwritten wrapper around the extracted measurement class. Reset/emplace and stable property ownership are admitted. The ignored final-metrics cache, ascent, relative-size propagation and return-reference lifetime remain outside this state projection. ReflowChild entry handling is a facade, not a complete extracted method.

Lean uses mathematical Int. The native corpus uses small representable values with zero/nonzero border padding and two different actual returned-size providers. Passing UBSan here does not bound general `nscoord` border sums, subtraction in cacheableB, physical conversion or native layout arithmetic. No all-writing-mode, all-frame-family, arbitrary lifecycle or full geometry API correctness is claimed.

The C++ comparisons are finite calibration of the source projection, not a theorem connecting arbitrary machine executions to Lean. Lean's standard library/kernel and the pinned external toolchain remain trusted inputs. The local Lean and clang executable hashes/versions are pinned; the system SDK, dynamic libraries and complete installed Lean library tree are not packaged.

## Observed versus illustrative keys

The main 192-row corpus uses illustrative small keys (including a 32→0 containing-block change). The `observed_sentinel_to_zero_witness` separately models the root-reported trace: computed size 1440×1920 appunits remains fixed, CB block value 1073741823 (NS_UNCONSTRAINEDSIZE) becomes 0, and a clean hidden measuring reflow publishes zero. Equality compares the sentinel as an opaque captured key value; the model does not interpret it as a finite containing-block extent. The theorem's recovery part remains conditional on a supplied fixed-block provider and forced reflow; it is not a claim that the provisional patch passes the browser. Root runtime receipts are external corroboration, not this capsule's own execution evidence.
