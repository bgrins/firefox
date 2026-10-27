# Isolated MathML repair comparison passed

Committed HEAD gives2 PASS/2 FAIL in the exact four-case landing WPT. With only the one-line MathML repair, all4 pass. Both visible controls remain passing, both hidden first-query failures improve, all candidate repeated/show/restore assertions pass, and no new failure appears. The baseline first-failure messages do not by themselves certify later assertions.

The two phases normalize25 sources to committed HEAD and guard34 sources. Only nsMathMLContainerFrame.cpp differs between phases. Final WPT bytes match proposal-v2, scoped lint exits0, both phase builds succeed and the raw results bind their source and binary hashes. ROOT-COMPARISON.json independently recounts the exact changes. The original root-block cases remain separate interaction tests; their behavior without block repair107 is not inferred.

Restoration independently restores all25 original bodies and removes the owned temporary WPT. Its build exits0. Root verifies the live HEAD/index/native/source snapshot equals BEFORE, prepared INPUTS and FINAL, checks all925 staged payloads, the nine existing tests,39 resource/support pins and temporary-test absence, then records both rebuilt binary hashes. Original working prototypes and accepted106–108 are preserved; float109 is not installed.

The MathML candidate remains unaccepted pending broader integration and final review. Existing readiness lemmas are conditional; their Size observation does not prove corrected x/y. The proposed rectangle/whole-provider extension addresses that model gap separately. No performance or whole-CSS correctness claim follows from these four cases. Build-monitor export KeyErrors are retained alongside successful build markers.
