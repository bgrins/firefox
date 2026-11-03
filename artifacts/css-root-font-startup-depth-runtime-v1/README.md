# Font-animation startup depth observations

Exact four-case fixture3749adf6 ran on retained ten-role candidate archive with logging disabled. These are observations on the selective-handoff/font-prerequisite diagnostic browser, not a clean-upstream comparison or accepted new fix.

All four leaf values are22px initially and after two frames/calibration. At depth2 expected leaf128px is reached after a background-only leaf restyle, with animated and literal root alike. At depth4 expected leaf512px is not reached: immediate leaf88px in both modes. Subsequent leaf-first reads report levels4/3/2/1 as88/184/128/64 for animated root and88/256/128/64 for literal root. These reads are ordered observations, not simultaneous snapshots. Root/plain controls are32/64 throughout. All post-restyle animation and KeyframeEffect identities are preserved, with paused progress0; literal root correctly has no animation.

This extends the observed stale-startup failure to inherited em dependency chains even without root animation. One unrelated restyle repairs depth2 but does not fully settle depth4. The fixture does not count native passes, establish convergence or prove a fixed-pass remedy.

Stored observations were extracted read-only before browser close. Full archive and exact fixture checks pass before/after. Browser closed; configuration reset to installed Firefox without launch. Owned process absence and profile inode verified;34,744,592 bytes removed. Loopback server exited normally. No native acceptance.
