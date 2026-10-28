# Release calibration of the standalone tree-counting WPT

The exact two test bodies from the sealed css-inline successor ran with byte-identical WPT harness files in installed Firefox158.0. Only local harness URLs and a completion callback differ. Random remains disabled and no preference was changed. Both tests reach the unitless-value assertion and fail with0/0/0 instead of20/30/20px. Their length-control computed-value and geometry assertions run first and pass, so these failures are independent of random support and calibrated against positive controls.

Harness status is0 and all fixtures were cleaned up. The owned tab and browser were closed. Full native/binary/research hashes, nested index and exact staged165 selection match before/after; installed release binary hashes/identities also match. This is file-document harness calibration, not a complete wptrunner run, candidate test or acceptance. The eventual one-Rust-file fix has two WPT pages, retaining twelve cases in total.
