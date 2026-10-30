This disabled runner observes the exact two frozen WPT pages (six callbacks) in installed Firefox 158 and retained portable Chrome 156. It combines the executed stock-nine completion bridge/receiver with the executed partial-base browser launch, inventory checks, Firefox relaunch admission and profile-scoped cleanup. No browser, HTTP server, native source, Git or current-state operation ran during preparation.

HTML and testharness.js are served byte-for-byte from the frozen taint and snapshot-preservation packages. Only testharnessreport.js is replaced by the unchanged reporting-only bridge. The bridge posts after page completion, preserves every callback message/stack, and navigates serially to the second page. It adds no style/timing reads. Runtime RESOURCES.json hashes the actual served map, including the bridge; raw request bytes and normalized page records are saved separately. A passing callback need not contain its full numeric trajectory because the frozen assertions emit diagnostic JSON only on failure.

Each browser uses a fresh owned empty profile and localhost-only server with random run ID and nonce, exact host/origin checks, bounded requests and a 240-second watchdog. No user.js, WPT profile preferences, CSS feature overrides, remote-debugging interface or user profile is used. Existing Firefox executable/XUL/application.ini pins and Chrome's entire retained portable inventory are checked before and after observation. This is not an enterprise-policy or prefs.js contents audit.

Cleanup is copied unchanged from the executed partial-base runner. It first terminates the owned launcher group. Firefox relaunch admission and cleanup require the exact private profile plus initial full URL/run ID/nonce, a matching group leader and only its admitted profile children; a repeated census precedes signaling. Remaining or unrecognized processes prevent profile deletion and leave an explicit incomplete result. Chrome retains the original owned process-group cleanup. There is no broad browser kill. HTTP handlers are joined before final receiver-error assessment.

Ordinary FAIL is retained as completed observation. execution_complete means all page reports arrived and cleanup completed without transport errors; all_callbacks_pass, all_endings_ok and suite_pass remain separate. Timeout, missing pages, setup failures and cleanup failure stay visible. No native acceptance or predetermined taint PASS is asserted.

Root can run the saved checks without launching browsers:

```
python3 -I -S -B artifacts/css-taint-preservation-installed-browsers-v1/check.py
python3 -I -S -B artifacts/css-taint-preservation-installed-browsers-v1/run.py --browser firefox
python3 -I -S -B artifacts/css-taint-preservation-installed-browsers-v1/run.py --browser chrome
```

After preserving disabled policy/manifest, root may set only execution_enabled=true and reseal, then run serially:

```
python3 -I -S -B artifacts/css-taint-preservation-installed-browsers-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-taint-preservation-installed-browsers-v1/run.py --browser chrome --run
```

Exclusive outputs are artifacts/css-taint-preservation-stock-firefox-runtime-1 and artifacts/css-taint-preservation-chrome-runtime-1. Root should independently join raw requests, exact roster/resources, capabilities/UA and cleanup before freezing either result. No browser-specific fixture or oracle changes are made.
