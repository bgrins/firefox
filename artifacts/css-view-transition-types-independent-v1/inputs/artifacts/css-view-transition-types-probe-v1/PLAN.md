# Initial view-transition type set probe

Tests synchronous initial set semantics and delete/clear selector membership.
Twenty-one cases: five predicted duplicate-deletion discrepancies and sixteen
controls. Startup, public iteration, membership, delete return value and direct
selector matching are checked against an independent JS Set. No rendering
flush or restyle result is inferred. Cleanup skips each transition and awaits
finished; ready rejection is handled. No production change yet.
