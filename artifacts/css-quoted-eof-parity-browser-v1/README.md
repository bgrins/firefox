# Parity browser pair

The same 18-case WPT, resources, preferences and relevant source inputs were
pinned before and after both runs. Only the intended Rust source and rebuilt
Firefox/XUL binaries differ. Four failures become passes; all 18 cases pass.
The integration diagnostic retains four separate escaped-terminal-quote
failures, so the aggregate command still exits 1. All 50 other outcome records
are unchanged. Root and independent final review compare the raw results by
file and subtest name. See PAIR-RESULT.json and the root acceptance record.
