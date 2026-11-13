Independent grid bundle outcome checks
======================================

The baseline reports and raw WPT events agree on all 703 focused and 2,947 alignment outcomes. The focused set contains 700 passing subtests; alignment preserves 11 file failures and 53 subtest failures. All 64 retained failure messages and 22 decoded failure PNGs also match the archived reference reports.

compare_reports.py compares exact test identities and statuses, rejects duplicate or incomplete event sets, and joins raw events to reports. compare_failure_details.py additionally checks assertion messages and screenshot hashes, authenticating each reported image hash against its decoded PNG. Eight negative controls retain rejection evidence.

Candidate and restored phases are pending. These scripts establish observed test results only; source restoration, binary identity, process cleanup, provider eligibility, full work counts, timing and repair acceptance remain separate gates.
