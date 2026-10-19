# Independent semantic repair review

Authenticate MANIFEST.json against FREEZE.json, then run `python3 check.py`. The checker authenticates all external producer inputs before reading source/proof/evidence. It independently enumerates theorem names, checks exact patches/composition, validates terminal fixture values using a front decoder, and verifies the retained source-replay outcome families.

For a new complete source-only relocated replay, use `python3 check.py --replay-output /private/tmp/quoted-eof-parity-review-NEW`. That path must not exist. Producer toolchain pins apply. No live Gecko, WPT, Git or browser state is changed. Evidence excludes build binaries/oleans. See REPORT.md for proposal approval and outstanding native acceptance gates.
