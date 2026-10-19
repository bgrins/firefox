# Registered inheritance independent review

Read REVIEW.md for the bounded source/spec/WPT conclusion and PAIR-REVIEW.json for the accepted corrected browser pair. Historical cleanup-error receipts are retained separately and are not acceptance evidence.

Run the source-only integrity/evidence checker with:

```sh
python3 -I -S /absolute/path/to/css-registered-inherit-invalid-independent-v1/check.py
```

The checker needs only Python's standard library. It checks a closed manifest, exact two-hunk source transformations on both retained bases, source/test pins, complete paired subtest and harness rosters, and the three expected result changes. It does not run Firefox, rebuild native code, or prove the review's semantic arguments. The manifest and checker require an externally authenticated FREEZE.json.

The review created no compiler or browser targets. The temporary standalone patch application directory was removed after its exact apply/reverse receipt was retained. All remaining files are source, specification/discovery records, review text or evidence.
