# System Firefox 158 sibling-count observation

The root-owned browser observation reproduces six mismatched values across
three mutation/recovery phases: the third target's width-count and opacity-count
use the other parent's count. Width geometry is 20px instead of 30px, then 30px
instead of 40px, then 20px instead of 30px. Opacity similarly reads 0.2/0.3/0.2
instead of 0.3/0.4/0.3. All 54 records satisfy the independent index/count,
literal-reference, repeat, equal-parent-style and zero-animation calibrations;
all 36 sibling-index/inherited-font-weight control records match.

No CSS preferences were changed, but preference readback was unavailable because
no privileged context was available. This is an observation in the existing
System Firefox 158 session, not proof of factory-default settings. No native
patch was applied. Root reports its owned tabs were closed after observation.

The first double-requestAnimationFrame attempt timed out and produced no valid
observation. The successful observer removes exactly that one await statement;
synchronous CSSOM/layout reads flush each mutation. verify.py checks this exact
delta and independently reconstructs all expected values and mismatch identities.
The connector rejected saveTo for the repository path; the actual successful
inline result was saved using workspace file tools. RESULT.json retains these
execution and transport limits. This archive does not prove a particular cache
path or the proposed repair, and makes no native acceptance or coverage claim.
