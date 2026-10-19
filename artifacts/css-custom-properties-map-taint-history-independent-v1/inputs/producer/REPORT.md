# Payload-and-taint history composition

This component instantiates the previously accepted LiveCount.CompareSound contract with TaintShortcut.metadata_same_sound. Its conclusion carries payload and attr taint through arbitrary key-update/COW histories to nearest-owner lookup and indexed enumeration. It is a mathematical model composition, not a new native translation proof.

Nine new results in TaintHistory.lean use twelve exact imported modules. No imported proof is edited. compare_sound discharges comparator soundness from the one-way PayloadSound contract; it does not assume native full-struct equality. lookup_reference and lookup_url allow an arbitrary initial modeled store. Indexed results start from LiveCount.initial and derive the iterator/count premises through accepted history theorems, rather than assuming raw enumeration. prefix_indexed_taint covers any finite prefix. exact_count needs no PayloadSound at all. Two concrete histories show why count correctness alone cannot preserve taint and show the corrected comparator carries taint.

The executable driver tests count, nearest-owner value and indexed value. Three compiled comparator-wiring mutants select payload-only equality or ignore one direction of taint change. Count and deletion controls remain correct while the intended lookup/index observations differ. They change no input data or expected observation. These are three new semantic wiring mutants, not a claimed rerun of all predecessor mutants. The nine new theorem axiom reports transitively include their imported dependencies. Predecessor acceptance and original full audit inventories remain separately sealed.

## Exact source-version transfer

SOURCE-TRANSFER.json and four complete source snapshots bind the prior combined map 9ce38cf9 to the taint candidate 58c66ad3. The checker verifies that only the map do_insert call changes from Option PartialEq to existing can_deduplicate_values. All storage/count/iterator/expansion/lookup bodies remain identical. It also binds the separate universal cascade comparison change to candidate 714f7d9a. This earlier gate is not executed by LiveCount.run: operations here are the already-computed optional values that reach the map. It is not valid to infer full declaration-history correctness merely from this theorem. The earlier taint capsule separately proves its admitted scalar two-stage contract.

## Limits

PayloadSound remains a semantic payload quotient premise; native equality omits url_data and other metadata. Arbitrary global PartialEq is not proved sound for the full native struct. Actual map admission still requires finite ordered unique-key nodes, faithful Arc/COW branch outcomes, immutable parent chains, membership/lookup agreement, machine headroom and native source-model correspondence. Whole CSSOM map composition requires consistent registration routing and disjoint inherited/reset domains. Substitution, state-dependent early-gate eligibility, active references and other observers remain external. No allocation/performance claim is made. URL observations are the prior selected full-taint scalar projection, not complete URL behavior.

The source transfer is exact text identity plus manually reviewed operation correspondence. Kernel checking cannot establish that correspondence, Rust compiler correctness or browser behavior. Root runtime evidence remains separate.
