# Attribute dependency admission review

Read REPORT.md for the independent spec oracle, narrow three-line collection repair and substantive formal scope proposal. Relative-unit metadata loss remains separate and its three runtime failures are retained.

After externally authenticating MANIFEST.json and check.py, run:

```sh
python3 -I -S -B check.py --manifest-sha <external manifest SHA256>
```

Replay authenticates all inputs first, checks exact source/test deltas, reparses retained root baseline/candidate logs and runs only `node --check` on the test script in a temporary directory. Node identity is pinned. It does not compile native code or run a browser. The capsule can be relocated; it does not read the live repository.
