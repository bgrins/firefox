# Selected-color V5 tracker lifetime correction

V4 candidate 50372/cbc269/d0eb31/1 failed E0106, build exit 2, no browser. The previous isolated tracker stub omitted AttributeTracker's internal lifetime and missed the actual type shape. V4 remains immutable.

V5 declares SubstitutionInput<'a, 'b> with Unresolved(&'a VariableValue, &'a mut AttributeTracker<'b>), and spells helper input SubstitutionInput<'_, '_>. The temporary input borrow and stored ElementContext lifetime are independent. Prepared remains owned static input without resubstitution. Every executable statement and both other postimages remain unchanged.

Searchfox746719/7719da and exact current declaration193701 confirmed the type. Root admission3af868 pins dom.rs22d0bf05 current=HEAD; REFERENCES pins that source receipt and excerpt. The revised analogue includes the exact tracker struct declaration, but substitutes ElementContext methods, AttributeReferences storage and computation. It is not a Stylo compile.

Actual checks: f0a02b/0 reproduces predecessor E0106 then six corrected tests pass, including tracker storage outliving the temporary input borrow. fc65db/0 verifies exact three replacements, clean patch forward/reverse and formatting. Scratch removed. Initial test generation c34998 accidentally changed result.0 to result.references; initial-analogue-error.log retains the test-only failure, corrected before final run without native postimage changes. Unchanged classifier16/4 evidence is inherited from V4, not rerun.

No native edit, Git/index/app, browser or build operation occurred. Actual Stylo compilation remains required. Exact42 suite unchanged; restoration and next owner admission remain separate root evidence.
