# Expanded original animation-taint baseline

The 120-case baseline completed with **103 PASS, 17 FAIL and 16 OK page endings**. Owner91618/e736db/0 and independent reviewer93375/b8e7f9/0 both completed successfully. All118 prior callback/page signatures are unchanged. The14 added callbacks yield5PASS/9FAIL: direct attr2FAIL/2PASS, nested fallback2FAIL/1PASS, inherited selection2FAIL/1PASS and registered scope3FAIL/1PASS.

The independent review replayed raw events against the exact roster, resources, metadata and application binding; checked current source, binary, application, index and control state; and verified the owned process group and temporary profile are absent. No native source or canonical coverage changed. These17 failing cases are not17 independent bug reports, and this baseline accepts no native fix.

The WPT tools directory is borrowed through the exact link recorded in SYMLINKS.json. FILES.json authenticates regular files without following that directory link.
