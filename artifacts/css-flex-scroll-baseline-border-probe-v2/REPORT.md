# Expanded scroll baseline diagnostic

The 288-row exploratory matrix includes flex and inline parent contexts and block, flex and grid scrolled contents. All removal/restoration and geometry checks pass in installed release.

Twenty-four release rows show the asymmetric-border defect in flex/grid scroll containers under direct or nested flex baseline alignment. These are ordinary last-baseline cases, with 9px start-only or end-only borders and hidden/auto/scroll overflow. The separate WPT restricts its oracle to the confirmed flex-parent behavior and expands writing modes and direction.

Another 24 diagnostic mismatches occur for inline block scroll containers. These involve the legacy baseline synthesis policy and are not counted as instances of the border defect. This exploratory page's `matched` field is not a blanket specification verdict. No claim is made that all 48 mismatches are bugs.

The development observation remains a shared-build diagnostic; exact repair causality is established separately by the pinned one-source WPT comparison.
