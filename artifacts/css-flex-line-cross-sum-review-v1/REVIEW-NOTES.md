# Working review notes

Initial working notes, superseded by REPORT.md and final authenticated evidence.

- GenerateFlexLines creates one initial line unconditionally, including an empty container; the changed count-minus-one expression therefore has a nonempty provider. nsTArray Length returns size_t from uint32 storage, giving count at most 4294967295.
- Nonnegative gap is a ResolveGapToLength / ResolveToLength<true> provider condition. ComputeCrossSizeAndBaseline's max includes largestOuterCrossSize initialized to zero; therefore line size is nonnegative under defined preceding arithmetic. Earlier provider calculations remain outside this sum-only repair.
- ApplyMinMaxBSize's default consumed argument is zero, but a sentinel max/min skips the corresponding clamp. Bounded min/max algebra alone does not cover absent maximum. New saturation can change old-defined values between nscoord_MAX and INT32_MAX. Example no-max two 720000000-au lines: old 1440000000, new 1073741823. This is intended range policy, not identity.
- Need cover all ComputeCrossSize observer branches: column, definite BSize without automatic minimum, containment ignore sum; auto row consumes optional min/max; automatic minimum takes max with computed BSize.
- Existing later CrossAxisPositionTracker subtraction/positioning arithmetic is a separate limitation. Passing the size oracle is not proof of the whole downstream layout path's integer safety.
- WPT uses one flex item per line, non-stretch alignment, logical cross sizes, both wrap directions and three writing modes. Supported-range checks only admit input values, then the size oracle is unconditional. Existing cases include small/no overflow, line sum, gap product and combined overflow. Empty and one-line cases are useful additional native boundary controls, not necessarily required browser expansion.

Primary specification checked 2026-10-20: https://drafts.csswg.org/css-flexbox-1/#algo-cross-container and https://drafts.csswg.org/css-values-4/#numeric-types . Content-based cross size uses flex-line sizes subject to formatting-context size constraints. Numeric implementation range limitations require calibrating large inputs before testing their small observable result.
