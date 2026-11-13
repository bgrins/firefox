# Baseline padding producer range contract

This contract follows the actual grid SetProp writer and the baseline-padding reader in SizeComputationInput::InitOffsets. PRODUCER.cpp and CONSUMER.cpp are exact excerpts from the retained local source files. Searchfox identifies the same writer upstream; the local snapshots define this contract's source identity.

encode follows the writer's branch order: select the offset only for content-baseline alignment, clamp a negative adjustment to zero, otherwise negate for last-baseline alignment. stored models removing zero-valued properties. magnitude follows the reader's positive/start versus nonpositive/end branch. Mathematical integers use a signed32 input bound supplied by current nscoord storage; the desired output fit is not assumed.

The sixteen obligations establish stored range, exclude minimum signed32 and zero from present properties, preserve first/last selection, derive adjustment and composite bounds, and exhibit jointly satisfying boundary inputs. The addition witness shows that valid signed32 inputs and safe negation do not guarantee subsequent padding addition fits signed32. This is a model witness, not established browser reachability.

Side and axis bounds assume original padding and border sides are signed32 and each axis receives at most one baseline contribution after padding initialization. The frozen function initializes padding before separately applying block and inline properties. Earlier theme conversions, style resolution, baseline-offset computation, pointer/property lifecycle, C++ semantics and browser reachability are not proved. Earlier undefined behavior would invalidate the connection to this model.

This writer cannot supply INT32_MIN to the reader's negation. This does not prove absence of other property mutation routes or complete containing-block migration. General nonnegativity of padding overrides remains open. Once storage/producers widen, their type-derived bounds must be revisited.

Acceptance requires unchanged target definitions and statements, Lean kernel checking with standard axioms only, concrete witnesses and independent source/target review. Native/binary refinement and protected comparator acceptance are outside this standalone model check.
