# Installed-browser registered defaulting observation

This disabled runner serves the exact three-case registered-defaulting WPT page with the pinned harness and a reporting-only completion bridge. It reuses the executed registered observer's browser admission, localhost transport, empty private profile, watchdog, Firefox relaunch admission, and owned cleanup without changes. No browser preference overrides or native application work is introduced.

The report retains raw records, WPT callback and harness status, copied fixture calibration checks, and a separate diagnostic comparison of sink outputs with `vertical-lr`. The invalid/valid variable sink comparison has no policy verdict. WPT PASS concerns registration, independent driver, valid-source and literal controls only; it does not establish the invalid keyframe's selected value or animation-taint behavior. The invalid custom property's computed trajectory is recorded before and after the ordinary change rather than asserted. Later custom/timing/membership fields are sequential diagnostics after the sink samples.

`execution_complete` means report transport and owned cleanup completed. `observation_complete`, reference checks, literal sink checks, WPT statuses and harness status remain separate. An ordinary WPT failure is retained and does not itself fail transport. Partial records from setup or harness timeouts remain incomplete. A blocked in-page promise has only the existing external watchdog; there is no promise of exporting every hung partial state.

The receiver validates structure and preserves wrong values. The reporter copies the fixture's exact `referenceChecks` function; a future independent replay should reconstruct it from raw records, not trust reported booleans. Served resource hashes, raw request bytes, report, process/cleanup and command/environment receipts are saved. Existing installed Firefox 158 and portable Chrome 156 pins are checked before and after actual execution; preparation checks read saved artifacts only.

After root reviews, enables the execution gate and reseals the owner, run serially:

```
python3 -I -S -B artifacts/css-animation-taint-registered-defaulting-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-animation-taint-registered-defaulting-installed-v1/run.py --browser chrome --run
```

The default command authenticates saved inputs without launching a browser. No browser has been run for this package. The fixture is sealed as `35ac9eda1a36f3552222f812db76eb22d97e3e850aaf887db4b32c4c71d90347`; the execution gate remains false.
