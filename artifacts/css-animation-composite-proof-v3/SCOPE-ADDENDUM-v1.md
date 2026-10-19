# Scope clarification v1

The approved SCOPE is retained in full. These requirements replace its ambiguous qualifiers.

1. Extract complete named-range `GetComputedOffset` and offset refresh logic. Timeline geometry is an explicit raw input provider with map/range premises; no named-range case is dropped. If this extraction fails, stop for root scope revision.
2. Extract complete `BuildSegmentsFromValueEntries`, missing-initial/final helpers, and segment equality. A prebuilt expected-segment provider is forbidden.
3. Extract complete `SetComposite` and `MaybeUpdateKeyframeComputedOffsets` entry functions and trace their actual context dispatch. Default/context actions in the native harness execute these functions.
4. Specified percentages are finite admitted inputs. Unresolved computed offsets use NaN separately. Native comparison and getter serialization controls include positive and negative zero.
5. Quotient allocation identity only under immutable declaration ownership plus structural equality/serialization congruence. Retain pointer-shortcut controls with stable payloads.
6. Extract the production `KeyframesEqualIgnoringComputedOffsets` by its full function name. The unchanged DEBUG `SpecifiedKeyframeArraysAreEqual` assertion omits composite and is not evidence of composite preservation. Observe clone/restore and getter composite directly.

Ordinary WAAPI is the universal boundary. CSS-generated augmentation, CSS override bookkeeping and Rust sampling retain the declared source trace/WPT boundaries.
